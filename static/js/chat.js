document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("chat-form");
  const input = document.getElementById("chat-input");
  const button = document.getElementById("send-btn");
  const history = document.getElementById("chat-history");
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";

  if (!form || !input || !button || !history) return;

  function appendMessage(text, type) {
    const message = document.createElement("div");
    const paragraph = document.createElement("p");
    message.className = `chat-message ${type}`;
    paragraph.textContent = text;
    message.appendChild(paragraph);
    history.appendChild(message);
    history.scrollTop = history.scrollHeight;
    return message;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text || button.disabled) return;

    appendMessage(text, "user");
    input.value = "";
    button.disabled = true;
    button.textContent = "Pensando…";
    const pending = appendMessage("Kady está preparando una respuesta…", "assistant");

    try {
      const payload = new FormData();
      payload.append("consulta", text);
      const response = await fetch("/consulta", {
        method: "POST",
        body: payload,
        credentials: "same-origin",
        headers: { "X-CSRF-Token": csrf },
      });
      const data = await response.json().catch(() => ({}));
      pending.remove();
      if (!response.ok) {
        appendMessage(data.error || "No fue posible procesar la consulta.", "assistant error");
        return;
      }
      appendMessage(data.mensaje || "No recibí una respuesta.", "assistant");
    } catch (_) {
      pending.remove();
      appendMessage("No se pudo conectar con el servidor.", "assistant error");
    } finally {
      button.disabled = false;
      button.textContent = "Enviar";
      input.focus();
    }
  }

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    sendMessage();
  });

  input.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  });
});
