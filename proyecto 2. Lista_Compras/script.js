const añadir = document.getElementById("añadir")
const lista = document.getElementById("lista")
const input = document.getElementById("input")

añadir.addEventListener("click", () => {
    const li = document.createElement("li")
    lista.appendChild(li)
})