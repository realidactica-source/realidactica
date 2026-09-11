document.addEventListener("DOMContentLoaded", () => {
  const questions = [
    { text: "Cuando descubres un tema nuevo, prefieres…", options: [["V", "Ver un diagrama o demostración"], ["A", "Escuchar una explicación"], ["K", "Probarlo paso a paso"]] },
    { text: "Para recordar una idea importante, te ayuda más…", options: [["V", "Subrayarla o convertirla en un mapa"], ["A", "Repetirla en voz alta"], ["K", "Relacionarla con una actividad"]] },
    { text: "En una clase compleja sueles…", options: [["V", "Observar ejemplos visuales"], ["A", "Seguir la explicación oral"], ["K", "Resolver un ejercicio mientras aprendes"]] },
    { text: "Cuando das instrucciones a alguien, normalmente…", options: [["V", "Dibujas o muestras dónde está cada cosa"], ["A", "Explicas con detalle"], ["K", "Acompañas a la persona y lo haces con ella"]] },
    { text: "Para prepararte para un examen eliges…", options: [["V", "Esquemas, colores y tarjetas"], ["A", "Explicarte el tema o escuchar notas"], ["K", "Ejercicios, simulaciones y práctica"]] },
    { text: "Una aplicación te resulta más fácil si…", options: [["V", "Tiene una interfaz clara"], ["A", "Incluye instrucciones habladas"], ["K", "Puedes explorarla sin miedo"]] },
    { text: "En un equipo aportas mejor cuando…", options: [["V", "Organizas la información"], ["A", "Dialogas y resumes acuerdos"], ["K", "Construyes y pruebas soluciones"]] },
    { text: "Al resolver un problema difícil prefieres…", options: [["V", "Representarlo gráficamente"], ["A", "Hablarlo con otra persona"], ["K", "Intentar distintas soluciones"]] },
  ];

  const questionBox = document.getElementById("quiz-question");
  const optionBox = document.getElementById("quiz-options");
  const resultBox = document.getElementById("quiz-result");
  const step = document.getElementById("quiz-step");
  const percent = document.getElementById("quiz-percent");
  const progress = document.getElementById("quiz-progress");
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";
  if (!questionBox || !optionBox || !resultBox || !step || !percent || !progress) return;

  const scores = { V: 0, A: 0, K: 0 };
  let current = 0;

  function renderQuestion() {
    const question = questions[current];
    questionBox.replaceChildren();
    optionBox.replaceChildren();
    const heading = document.createElement("h2");
    heading.textContent = question.text;
    questionBox.appendChild(heading);
    step.textContent = `Pregunta ${current + 1} de ${questions.length}`;
    percent.textContent = `${Math.round(((current + 1) / questions.length) * 100)}%`;
    progress.value = current + 1;

    question.options.forEach(([type, text], index) => {
      const button = document.createElement("button");
      button.type = "button";
      button.className = "quiz-option";
      const key = document.createElement("span");
      key.textContent = String.fromCharCode(65 + index);
      const label = document.createElement("strong");
      label.textContent = text;
      button.append(key, label);
      button.addEventListener("click", () => choose(type));
      optionBox.appendChild(button);
    });
  }

  function choose(type) {
    scores[type] += 1;
    current += 1;
    if (current < questions.length) renderQuestion();
    else saveResult();
  }

  async function saveResult() {
    questionBox.replaceChildren();
    optionBox.replaceChildren();
    const total = questions.length;
    const values = {
      v: Math.round((scores.V / total) * 100),
      a: Math.round((scores.A / total) * 100),
      k: Math.round((scores.K / total) * 100),
    };
    const dominantKey = Object.entries(scores).sort((first, second) => second[1] - first[1])[0][0];
    const labels = { V: "Visual", A: "Auditivo", K: "Kinestésico" };
    values.dominante = labels[dominantKey];

    try {
      const response = await fetch("/guardar_resultado", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
        body: JSON.stringify(values),
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || "No se pudo guardar el resultado.");
      renderResult(values);
    } catch (error) {
      resultBox.hidden = false;
      const message = document.createElement("p");
      message.textContent = error instanceof Error ? error.message : "No se pudo guardar el resultado.";
      resultBox.replaceChildren(message);
    }
  }

  function renderResult(values) {
    resultBox.hidden = false;
    resultBox.replaceChildren();
    const eyebrow = document.createElement("span");
    eyebrow.className = "eyebrow";
    eyebrow.textContent = "Tu resultado";
    const orb = document.createElement("div");
    orb.className = "result-orb";
    orb.textContent = values.dominante.slice(0, 1);
    const heading = document.createElement("h2");
    heading.textContent = `Tu estilo dominante es ${values.dominante}`;
    const paragraph = document.createElement("p");
    paragraph.className = "muted";
    paragraph.textContent = "Este resultado es una orientación, no una etiqueta. Combinar estilos fortalece el aprendizaje.";
    const bars = document.createElement("div");
    bars.className = "result-bars";
    [["Visual", values.v], ["Auditivo", values.a], ["Kinestésico", values.k]].forEach(([label, value]) => {
      const meter = document.createElement("div");
      meter.className = "meter";
      const info = document.createElement("div");
      const name = document.createElement("span");
      name.textContent = label;
      const number = document.createElement("strong");
      number.textContent = `${value}%`;
      info.append(name, number);
      const bar = document.createElement("progress");
      bar.max = 100;
      bar.value = value;
      meter.append(info, bar);
      bars.appendChild(meter);
    });
    const link = document.createElement("a");
    link.className = "btn btn-primary";
    link.href = "/perfil";
    link.textContent = "Ver mi perfil";
    resultBox.append(eyebrow, orb, heading, paragraph, bars, link);
  }

  renderQuestion();
});
