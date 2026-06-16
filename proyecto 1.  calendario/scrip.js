const derecha = document.getElementById("derecha")
const izquierda = document.getElementById("izquierda")
const dibujar_meses = document.getElementById("meses")
const dias_dibujar = [
    document.getElementById('1'),
    document.getElementById('2'),
    document.getElementById('3'),
    document.getElementById('4'),
    document.getElementById('5'),
    document.getElementById('6'),
    document.getElementById('7'),
    document.getElementById('8'),
    document.getElementById('9'),
    document.getElementById('10'),
    document.getElementById('11'),
    document.getElementById('12'),
    document.getElementById('13'),
    document.getElementById('14'),
    document.getElementById('15'),
    document.getElementById('16'),
    document.getElementById('17'),
    document.getElementById('18'),
    document.getElementById('19'),
    document.getElementById('20'),
    document.getElementById('21'),
    document.getElementById('22'),
    document.getElementById('23'),
    document.getElementById('24'),
    document.getElementById('25'),
    document.getElementById('26'),
    document.getElementById('27'),
    document.getElementById('28'),
    document.getElementById('29'),
    document.getElementById('30'),
    document.getElementById('31'),
    document.getElementById('32'),
    document.getElementById('33'),
    document.getElementById('34'),
    document.getElementById('35')
]

const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const dias_meses = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
let mes_actual = 0
let dias_mes = 0


function colocar_dias(dias) {
    // Limpia todos los días
    dias_dibujar.forEach(element => {
        element.textContent = "";
    });

    let dias_mes_actual = dias_meses[dias]; // cantidad de días del mes

    for (let i = 0; i < dias_dibujar.length; i++) {
        if (i < dias_mes_actual) {
            dias_dibujar[i].className = 'dia'
            dias_dibujar[i].textContent = i + 1;
        } else {
            dias_dibujar[i].className = 'dia siguiente'
            dias_dibujar[i].textContent = i - dias_mes_actual + 1;
        }
    }
}


dibujar_meses.textContent = meses[mes_actual]
colocar_dias(dias_mes)


derecha.addEventListener("click", () => {
    mes_actual++
    dias_mes++
    if (mes_actual > meses.length - 1){
        mes_actual = 0
        dias_mes = 0
    }
    dibujar_meses.textContent = meses[mes_actual]
    colocar_dias(dias_mes)
})

izquierda.addEventListener("click", () => {
    mes_actual--
    dias_mes--
    if (mes_actual < 0 || dias_mes < 0){
        mes_actual = meses.length - 1
        dias_mes = dias_meses.length -1
    }
    dibujar_meses.textContent = meses[mes_actual]
    colocar_dias(dias_mes)
})