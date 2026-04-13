document.addEventListener('DOMContentLoaded', () => {
    // Referencias del DOM para Drag & Drop
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('quick-pdf-upload');
    const fileNameDisplay = document.getElementById('file-name-display');
    const btnAssign = document.getElementById('btn-quick-assign');
    const selectCarrera = document.getElementById('quick-carrera');
    const inputGrupo = document.getElementById('quick-grupo');
    
    // Referencias para la barra de progreso
    const progressContainer = document.getElementById('upload-progress-container');
    const progressFill = document.getElementById('upload-progress-fill');
    const progressText = document.getElementById('upload-status-text');

    // Manejar la selección manual de archivo
    fileInput.addEventListener('change', (e) => {
        handleFiles(e.target.files);
    });

    // Eventos de Drag & Drop
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            // Validar que sea PDF
            if(e.dataTransfer.files[0].type === "application/pdf" || e.dataTransfer.files[0].name.endsWith('.pdf')) {
                fileInput.files = e.dataTransfer.files; 
                handleFiles(e.dataTransfer.files);
            } else {
                alert('⚠️ Por favor, sube únicamente archivos PDF.');
            }
        }
    });

    // Función para mostrar el nombre del archivo
    function handleFiles(files) {
        if (files.length > 0) {
            const fileName = files[0].name;
            fileNameDisplay.innerHTML = `<i class="fa-solid fa-check" style="color: var(--neon-green);"></i> Archivo listo: <strong>${fileName}</strong>`;
            fileNameDisplay.style.color = '#fff';
            dropZone.style.borderColor = 'var(--neon-green)';
        } else {
            resetUploadZone();
        }
    }

    // Resetear la zona visualmente
    function resetUploadZone() {
        fileNameDisplay.innerHTML = 'Arrastra tu archivo PDF aquí o haz clic para explorar';
        fileNameDisplay.style.color = 'var(--text-gray)';
        dropZone.style.borderColor = 'var(--neon-blue)';
        fileInput.value = '';
    }

    // Acción del botón de asignar con simulación de progreso
    btnAssign.addEventListener('click', () => {
        const file = fileInput.files[0];
        const carrera = selectCarrera.options[selectCarrera.selectedIndex].text;
        const grupo = inputGrupo.value.trim();

        // Validaciones básicas
        if (!file) {
            alert('⚠️ Por favor, selecciona un archivo PDF primero.');
            return;
        }
        if (selectCarrera.value === "" || grupo === "") {
            alert('⚠️ Por favor, selecciona la carrera e ingresa el grupo de destino.');
            return;
        }

        // Iniciar simulación de subida
        btnAssign.disabled = true;
        const originalText = btnAssign.innerHTML;
        btnAssign.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Procesando...';
        btnAssign.style.opacity = '0.7';
        
        // Mostrar barra de progreso
        progressContainer.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.innerText = '0%';

        let progress = 0;
        
        // Simular el tiempo de carga hacia tu backend
        const uploadInterval = setInterval(() => {
            progress += Math.random() * 15; // Incrementar aleatoriamente
            if (progress > 100) progress = 100;
            
            progressFill.style.width = `${progress}%`;
            progressText.innerText = `${Math.floor(progress)}%`;

            if (progress === 100) {
                clearInterval(uploadInterval);
                
                setTimeout(() => {
                    alert(`✅ ¡Material subido con éxito al servidor!\n\nArchivo: ${file.name}\nDestino: ${grupo} - ${carrera}\n\nListo para ser consumido por la plataforma educativa.`);
                    
                    // Limpiar el formulario después del éxito
                    resetUploadZone();
                    selectCarrera.value = "";
                    inputGrupo.value = "";
                    btnAssign.innerHTML = originalText;
                    btnAssign.disabled = false;
                    btnAssign.style.opacity = '1';
                    
                    // Ocultar barra de progreso
                    progressContainer.style.display = 'none';
                    progressFill.style.width = '0%';
                    
                }, 500);
            }
        }, 300);
    });
});