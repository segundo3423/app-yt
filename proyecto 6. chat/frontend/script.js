
const contenedorMensajes = document.querySelector('.contenedorMensajes');
const inputMensaje = document.querySelector('.inputMensaje');
const btnEnviar = document.querySelector('.btnEnviar');
const formulario = document.querySelector('.formulario');

const quitar = document.querySelector('.quitar');
const barraLateral = document.querySelector('.barraLateral');

let ocultar = false;
quitar.addEventListener('click', () => {
    if (quitar.style.transform === "scaleX(-1)") {
        quitar.style.transform = "scaleX(1)";
    } else {
        quitar.style.transform = "scaleX(-1)";
    }
    barraLateral.style.display = ocultar ? 'flex' : 'none';
    ocultar = !ocultar;
});

formulario.addEventListener('submit', (e) => {
    e.preventDefault();
    const mensaje = inputMensaje.value.trim();
    if (mensaje) {
        const li = document.createElement('li');
        li.textContent = mensaje;
        contenedorMensajes.appendChild(li);
        formulario.reset();
    }
});