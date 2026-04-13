document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('chat-input');
    const btn = document.getElementById('send-btn');
    const history = document.getElementById('chat-history');
    
    // Detectamos la materia desde el body (ej: calculo, redes, general)
    const materiaActual = document.body.getAttribute('data-materia') || "general";

    async function enviar() {
        const texto = input.value.trim();
        if(!texto) return;

        // Mostrar mensaje del usuario
        appendMessage(texto, 'user-msg');
        input.value = '';

        const formData = new FormData();
        formData.append('consulta', texto);
        formData.append('materia', materiaActual); // Enviar contexto al servidor

        try {
            const res = await fetch('/consulta', { method: 'POST', body: formData });
            const data = await res.json();
            
            // Mostrar respuesta de la IA
            appendMessage(data.mensaje, 'bot-msg');
        } catch (e) {
            appendMessage("Error: No se pudo conectar con el servidor.", 'bot-msg');
        }
    }

    function appendMessage(texto, tipo) {
        const p = document.createElement('p');
        p.classList.add('chat-bubble', tipo);
        p.textContent = texto;
        history.appendChild(p);
        history.scrollTop = history.scrollHeight;
    }

    btn.addEventListener('click', enviar);
    input.addEventListener('keypress', (e) => {
        if(e.key === 'Enter') enviar();
    });
});