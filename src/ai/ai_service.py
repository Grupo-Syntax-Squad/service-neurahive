import requests
import json
from collections import deque
from typing import Deque, Literal, TypedDict

from src.database.models import Agent

AI_API_KEY = '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'
AI_API_URL = 'https://openrouter.ai/api/v1/chat/completions'

headers = {
    'Authorization': f'Bearer {AI_API_KEY}',
    'Content-Type': 'application/json'
}


class Message(TypedDict):
    role: Literal["system", "user", "assistant"]
    content: str


# Cria a fila com limite de 20 mensagens (10 interações user + assistant)
conversation_history: Deque[Message] = deque(maxlen=20)


def send_message(agent: Agent, pergunta_usuario: str) -> str:
    with open('example.json', 'r', encoding='utf-8') as f:
        faq_data = json.load(f)

    faq_context = "\n".join([
        f"Pergunta: {item['pergunta']}\nResposta: {item['resposta']}"
        for item in faq_data["faq"]
    ])

    global conversation_history

    conversation_history.append({"role": "user", "content": pergunta_usuario})

    system_message = {
        "role": "system",
        "content": (
            f"Você é um assistente que responde apenas sobre o tema {agent.theme}, em pt-br, com base nas perguntas e respostas abaixo."
            f"Se a pergunta não estiver presente ou relacionada ao conteúdo fornecido, diga que só pode responder perguntas sobre o tema {agent.theme}, "
            "diga qual o tema e não fale sobre nada relacionado à pergunta do usuário e nesse caso pode ser uma resposta mais curta."
            f"{agent.behavior} \n\n"
            f"{faq_context}"
        )
    }

    messages = [system_message] + list(conversation_history)

    data = {
        "model": "google/gemini-pro",
        "messages": messages,
        "temperature": 0.5,  # Variedade nas respostas
        "top_p": 1.0,  # Garante respostas variadas e criativas
        "n": 1,  # Uma resposta por vez
        "stream": False,  # Resposta completa de uma vez
        "max_tokens": 500
    }

    response = requests.post(AI_API_URL, json=data, headers=headers)

    if response.status_code == 200:
        result = response.json()
        resposta_assistente: str = result['choices'][0]['message']['content']
        conversation_history.append({"role": "assistant", "content": resposta_assistente})
        return (resposta_assistente)
    else:
        return (f"Falha ao buscar dados da API. Código de Status: {response.status_code}")