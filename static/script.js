// Espera a que el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function () {
    // Cargar los datos del JSON para los departamentos, provincias y distritos
    fetch('/static/ubigeoPeru.json')
        .then(response => response.json())
        .then(data => {
            window.ubigeoPeru = data;
            cargarDepartamentos();
        })
        .catch(error => console.error('Error al cargar el JSON:', error));
});

// Cargar los departamentos en el select
function cargarDepartamentos() {
    const departamentoSelect = document.getElementById("departamento");
    for (const departamento in ubigeoPeru) {
        const option = document.createElement("option");
        option.value = departamento;
        option.text = departamento;
        departamentoSelect.add(option);
    }
}

// Cargar las provincias cuando se selecciona un departamento
function cargarProvincias() {
    const departamentoSelect = document.getElementById("departamento").value;
    const provinciaSelect = document.getElementById("provincia");
    provinciaSelect.innerHTML = '<option value="">Seleccionar Provincia</option>'; // Limpiar opciones anteriores
    const distritoSelect = document.getElementById("distrito");
    distritoSelect.innerHTML = '<option value="">Seleccionar Distrito</option>'; // Limpiar distritos
    if (departamentoSelect !== "") {
        const provincias = ubigeoPeru[departamentoSelect];
        for (const provincia in provincias) {
            const option = document.createElement("option");
            option.value = provincia;
            option.text = provincia;
            provinciaSelect.add(option);
        }
    }
}

// Cargar los distritos cuando se selecciona una provincia
function cargarDistritos() {
    const departamentoSelect = document.getElementById("departamento").value;
    const provinciaSelect = document.getElementById("provincia").value;
    const distritoSelect = document.getElementById("distrito");
    distritoSelect.innerHTML = '<option value="">Seleccionar Distrito</option>'; // Limpiar opciones anteriores
    if (provinciaSelect !== "") {
        const distritos = ubigeoPeru[departamentoSelect][provinciaSelect];
        distritos.forEach(function (distrito) {
            const option = document.createElement("option");
            option.value = distrito;
            option.text = distrito;
            distritoSelect.add(option);
        });
    }
}

// Función para mostrar u ocultar el campo de texto basado en la selección de un checkbox
// Función para mostrar u ocultar el campo de texto basado en la selección de un checkbox
function toggleOther(checkboxId, inputId, extraInputId = null) {
    var checkbox = document.getElementById(checkboxId);
    var input = document.getElementById(inputId);
    var extraInput = extraInputId ? document.getElementById(extraInputId) : null;

    if (checkbox.checked) {
        input.style.display = 'block';
        if (extraInput) {
            extraInput.style.display = 'block';
        }
    } else {
        input.value = ''; // Limpiar el campo si se deselecciona
        input.style.display = 'none';
        if (extraInput) {
            extraInput.value = ''; // Limpiar el campo si se deselecciona
            extraInput.style.display = 'none';
        }
    }
}


// Función para mostrar u ocultar el campo de texto basado en la selección de un radio button
function toggleOtherRadio(radioId, inputId) {
    var radios = document.getElementsByName(radioId);
    var input = document.getElementById(inputId);
    var isOtherSelected = false;

    radios.forEach(function(radio) {
        if (radio.checked && (radio.value === 'Sí se vincula' || radio.value === 'Sí está vinculado' || radio.value === 'Sí participa')) {
            isOtherSelected = true;
        }
    });

    if (isOtherSelected) {
        input.style.display = 'block';
    } else {
        input.value = ''; // Limpiar el campo si no se selecciona "Sí"
        input.style.display = 'none';
    }
}

// CONSULTA AJAX PARA OBJETIVO ESPECIFICO, NUMERO DE FORMULARIOS y COMPONENTES:
function fetchIniciativaData(nombre_iniciativa) {
    if (nombre_iniciativa) {
        // Fetch para el objetivo específico y el número de formularios
        fetch('/get_objetivo_especifico/' + nombre_iniciativa)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Asignar el objetivo específico
                    document.getElementById('objetivo_especifico').value = data.objetivo_especifico || '';
                    
                    // Mostrar el número de formulario
                    document.getElementById('numero_formulario').innerText = data.numero_formularios;
                    document.getElementById('numero_formulario_container').style.display = 'block';
                }
            })
            .catch(error => console.log('Error:', error));

        // Fetch para los componentes
        fetch('/get_componentes/' + nombre_iniciativa)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Asignar los componentes
                    document.getElementById('componente_1').value = data.componente_1 || '';
                    document.getElementById('componente_2').value = data.componente_2 || '';
                    document.getElementById('componente_3').value = data.componente_3 || '';
                }
            })
            .catch(error => console.log('Error:', error));
    } else {
        // Limpiar campos si no se selecciona una iniciativa
        document.getElementById('objetivo_especifico').value = '';
        document.getElementById('componente_1').value = '';
        document.getElementById('componente_2').value = '';
        document.getElementById('componente_3').value = '';
        document.getElementById('numero_formulario').innerText = '';
        document.getElementById('numero_formulario_container').style.display = 'none';
    }
}


// CONSULTA AJAX PARA OBTENER NUMERO DE FORMULARIOS CREADOS PARA CASOS EMBLEMATICOS
function fetchCasoEmblematicoData(nombre_caso) {
    if (nombre_caso) {
        fetch('/get_numero_formulario/' + nombre_caso)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    document.getElementById('numero_formulario').innerText = data.numero_formularios;
                    document.getElementById('numero_formulario_container').style.display = 'block';
                }
            })
            .catch(error => console.log('Error:', error));
    } else {
        document.getElementById('numero_formulario').innerText = '';
        document.getElementById('numero_formulario_container').style.display = 'none';
    }
}


// CONSULTA AJAX PARA OBTENER NUMERO DE FORMULARIOS CREADOS PARA nombre_politica_memoria
function fetchPoliticaMemoriaData(nombre_politica_memoria) {
    if (nombre_politica_memoria) {
        fetch('/get_numero_formulario_politica/' + nombre_politica_memoria)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(data.error);
                } else {
                    // Mostrar el número de formulario
                    document.getElementById('numero_formulario').innerText = data.numero_formulario;
                    document.getElementById('numero_formulario_container').style.display = 'block';
                }
            })
            .catch(error => console.log('Error:', error));
    } else {
        // Limpiar el número de formulario si no se selecciona una política
        document.getElementById('numero_formulario').innerText = '';
        document.getElementById('numero_formulario_container').style.display = 'none';
    }
}


// FUNCION PARA LA ALERTA QUE DESAPAREZCA EN LA PARTE SUPERIOR AL GUARDAR REGISTRO
setTimeout(function() {
    let alertElement = document.querySelector('.alert_mod');
    if (alertElement) {
        alertElement.style.transition = "opacity 0.5s ease";
        alertElement.style.opacity = "0";
        setTimeout(function() {
            alertElement.style.display = 'none';
        }, 500); // Da tiempo para que la transición se complete antes de eliminarla
    }
}, 3000); // Tiempo en milisegundos (5 segundos)
