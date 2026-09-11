document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("material-form");
  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("quick-pdf-upload");
  const fileLabel = document.getElementById("file-name-display");
  const group = document.getElementById("quick-grupo");
  const button = document.getElementById("btn-quick-assign");
  const status = document.getElementById("upload-status");
  const csrf = document.querySelector('meta[name="csrf-token"]')?.content || "";
  if (!form || !dropZone || !fileInput || !fileLabel || !group || !button || !status) return;

  let selectedFile = null;

  function setStatus(message, type = "") {
    status.className = `upload-status ${type}`.trim();
    status.textContent = message;
  }

  function selectFile(file) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      selectedFile = null;
      fileLabel.textContent = "Selecciona únicamente archivos PDF.";
      setStatus("Formato no permitido.", "error");
      return;
    }
    if (file.size > 15 * 1024 * 1024) {
      selectedFile = null;
      fileLabel.textContent = "El archivo supera 15 MB.";
      setStatus("Archivo demasiado grande.", "error");
      return;
    }
    selectedFile = file;
    fileLabel.textContent = `Listo: ${file.name}`;
    setStatus("Archivo validado en el navegador.");
  }

  fileInput.addEventListener("change", () => selectFile(fileInput.files?.[0]));
  ["dragenter", "dragover"].forEach((name) => dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    dropZone.classList.add("dragover");
  }));
  ["dragleave", "drop"].forEach((name) => dropZone.addEventListener(name, (event) => {
    event.preventDefault();
    dropZone.classList.remove("dragover");
  }));
  dropZone.addEventListener("drop", (event) => selectFile(event.dataTransfer?.files?.[0]));

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!selectedFile || !group.value) {
      setStatus("Selecciona un PDF y un grupo de destino.", "error");
      return;
    }
    const payload = new FormData();
    payload.append("archivo", selectedFile, selectedFile.name);
    payload.append("grupo_id", group.value);
    button.disabled = true;
    button.textContent = "Asignando…";
    setStatus("Subiendo y validando el material…");
    try {
      const response = await fetch("/api/materiales", {
        method: "POST",
        body: payload,
        credentials: "same-origin",
        headers: { "X-CSRF-Token": csrf },
      });
      const data = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(data.error || "No fue posible guardar el material.");
      setStatus(data.mensaje || "Material asignado.", "success");
      form.reset();
      selectedFile = null;
      fileLabel.textContent = "Arrastra un archivo aquí o usa el selector.";
    } catch (error) {
      setStatus(error instanceof Error ? error.message : "No fue posible guardar el material.", "error");
    } finally {
      button.disabled = false;
      button.textContent = "Asignar material";
    }
  });
});
