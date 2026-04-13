// Supongamos que estas variables acumulan los puntos A, B, C
let puntos = { A: 0, B: 0, C: 0 }; 

function answer(opcion) {
    puntos[opcion]++;
    // Lógica para pasar de pregunta...
    // Cuando llegues al final, llama a:
    finalizarTest();
}

function finalizarTest() {
    const total = puntos.A + puntos.B + puntos.C;
    const data = {
        v: Math.round((puntos.A / total) * 100),
        a: Math.round((puntos.B / total) * 100),
        k: Math.round((puntos.C / total) * 100),
        dominante: ""
    };

    // Determinar dominante
    if (data.v >= data.a && data.v >= data.k) data.dominante = "Visual";
    else if (data.a >= data.v && data.a >= data.k) data.dominante = "Auditivo";
    else data.dominante = "Kinestésico";

    // ENVIAR A LA BASE DE DATOS
    fetch('/guardar_resultado', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(res => {
        console.log(res.mensaje);
        window.location.href = "/prin.html"; // Redirigir al terminar
    });
}