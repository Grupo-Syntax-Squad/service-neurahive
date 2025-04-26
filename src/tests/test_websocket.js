const socket = new WebSocket("ws://localhost:8000/ws/chat")

socket.onopen = () => {
    console.log("Conectado!")
    socket.send("{}")
}

socket.onmessage = (event) => {
    console.log("Mensagem recebida:", event.data)
}

socket.onerror = (event) => {
    console.error("Erro no WebSocket:", event)
}

socket.onclose = (event) => {
    console.log("Conexão fechada!")
    console.log("Código de fechamento:", event.code)
    console.log("Motivo:", event.reason)
}
