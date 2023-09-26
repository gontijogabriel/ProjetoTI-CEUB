// Obtém o pathname da URL atual
var pathname = window.location.pathname;

console.log(pathname);

// Função para adicionar classe a um elemento se ele existir
function addClassIfElementExists(elementId, className) {
    var elemento = document.getElementById(elementId);
    if (elemento) {
        elemento.classList.add(className);
    }
}

// Verifica se o pathname corresponde a uma rota conhecida e adiciona a classe se o elemento existir
if (pathname == "/index.html") {
    addClassIfElementExists("index", "actived");
}

if (pathname == "/boletos_pagos.html") {
    addClassIfElementExists("pagos", "actived");
}

if (pathname == "/novo_boleto.html") {
    addClassIfElementExists("new", "actived");
}

if (pathname == "/configuracao.html") {
    addClassIfElementExists("configuracao", "actived");
}