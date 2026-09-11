import unittest
from unittest.mock import patch

import app as app_module

app = app_module.app


class RealidacticaSmokeTests(unittest.TestCase):
    def setUp(self) -> None:
        app.config.update(TESTING=True, SECRET_KEY="test-only-secret")
        self.client = app.test_client()

    def login_as(self, role: str) -> str:
        token = "csrf-test-token"
        with self.client.session_transaction() as session:
            session.update(
                loggedin=True,
                user_id=1,
                user_name="Prueba",
                user_rol=role,
                _csrf_token=token,
                chat_history=[],
            )
        return token

    def test_public_pages_and_security_headers(self) -> None:
        for path in ("/", "/login", "/registro", "/health"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)
            self.assertIn("Content-Security-Policy", response.headers)
            self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
            self.assertEqual(response.headers["X-Frame-Options"], "DENY")

    def test_class_pdf_can_only_be_framed_by_same_origin(self) -> None:
        response = self.client.get("/static/clases/calculo/integrales.pdf")
        try:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.headers["X-Frame-Options"], "SAMEORIGIN")
            self.assertIn("frame-ancestors 'self'", response.headers["Content-Security-Policy"])
        finally:
            response.close()

    def test_student_pages_render(self) -> None:
        self.login_as("alumno")
        for path in ("/prin", "/encuesta", "/clase/calculo", "/clase/frameworks", "/clase/liderazgo"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 200, path)

    def test_role_boundaries(self) -> None:
        self.login_as("alumno")
        self.assertEqual(self.client.get("/prin_m").status_code, 403)
        self.assertEqual(self.client.get("/portal-maestro").status_code, 403)

    def test_csrf_is_required_for_logout(self) -> None:
        token = self.login_as("alumno")
        self.assertEqual(self.client.post("/logout").status_code, 400)
        response = self.client.post("/logout", data={"_csrf_token": token})
        self.assertEqual(response.status_code, 302)

    def test_registration_does_not_offer_teacher_role(self) -> None:
        response = self.client.get("/registro")
        self.assertNotIn(b'value="maestro"', response.data)

    def test_demo_accounts_are_explicit_and_role_scoped(self) -> None:
        demo_env = {
            "DEMO_STUDENT_USERNAME": "alumno.demo",
            "DEMO_STUDENT_PASSWORD": "student-test-password",
            "DEMO_TEACHER_USERNAME": "maestro.demo",
            "DEMO_TEACHER_PASSWORD": "teacher-test-password",
        }
        with patch.object(app_module, "DEMO_MODE", True), patch.dict("os.environ", demo_env):
            response = self.client.get("/login")
            with self.client.session_transaction() as session:
                token = session["_csrf_token"]
            response = self.client.post(
                "/login",
                data={"usuario": "alumno.demo", "password": "student-test-password", "_csrf_token": token},
            )
            self.assertEqual(response.status_code, 302)
            self.assertTrue(response.headers["Location"].endswith("/prin"))


if __name__ == "__main__":
    unittest.main()
