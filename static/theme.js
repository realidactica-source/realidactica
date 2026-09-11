(() => {
  const root = document.documentElement;
  let savedTheme = null;
  try {
    savedTheme = localStorage.getItem("realidactica-theme");
  } catch (_) {
    savedTheme = null;
  }

  const preferred = window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  const initial = savedTheme === "light" || savedTheme === "dark" ? savedTheme : preferred;
  root.dataset.theme = initial;

  function updateButton(button) {
    const isDark = root.dataset.theme === "dark";
    const icon = button.querySelector("[data-theme-icon]");
    const label = button.querySelector("[data-theme-label]");
    if (icon) icon.textContent = isDark ? "☀" : "☾";
    if (label) label.textContent = isDark ? "Modo claro" : "Modo oscuro";
    button.setAttribute("aria-label", isDark ? "Activar modo claro" : "Activar modo oscuro");
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("[data-theme-toggle]").forEach((button) => {
      updateButton(button);
      button.addEventListener("click", () => {
        root.dataset.theme = root.dataset.theme === "dark" ? "light" : "dark";
        try {
          localStorage.setItem("realidactica-theme", root.dataset.theme);
        } catch (_) {
          // La preferencia sigue activa durante la sesión aunque el navegador bloquee el almacenamiento.
        }
        document.querySelectorAll("[data-theme-toggle]").forEach(updateButton);
      });
    });
  });
})();
