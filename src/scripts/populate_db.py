from sqlalchemy import text
from sqlalchemy.orm import Session
from src.database.get_db import get_db
from src.database.models import Agent, Chat, KnowledgeBase, User


class PopulateDatabase:
    def __init__(self) -> None:
        self._session = get_db()
        self._users: list[User] | None = None
        self._agents: list[Agent] | None = None
        self._chats: list[Chat] | None = None
        self._knowledge_bases: list[KnowledgeBase] | None

    def execute(self) -> None:
        with self._session as session:
            self._truncate_all_tables(session)

            self._initialize_users()
            self._populate_users(session)

            self._initialize_knowledge_bases()
            self._populate_knowledge_bases(session)

            self._initialize_agents()
            self._populate_agents(session)

            self._initialize_chats()
            self._populate_chats(session)

    def _truncate_all_tables(self, session: Session) -> None:
        session.execute(text('TRUNCATE TABLE agent, "user" RESTART IDENTITY CASCADE;'))
        session.commit()

    def _initialize_users(self) -> None:
        self._users = [
            User(
                role=[1, 2, 3],
                name="Admin user",
                email="admin@neurahive.com",
                password="admin",
                agents=[],
            ),
            User(
                role=[2, 3],
                name="Curator user",
                email="curator@neurahive.com",
                password="curator",
                agents=[],
            ),
            User(
                role=[3],
                name="Client user 1",
                email="client1@neurahive.com",
                password="client1",
                agents=[],
            ),
            User(
                role=[3],
                name="Client user 2",
                email="client2@neurahive.com",
                password="client2",
                agents=[],
            ),
            User(
                role=[3],
                name="Client user 3",
                email="client3@neurahive.com",
                password="client3",
                agents=[],
            ),
            User(
                role=[3],
                name="Client user 4",
                email="client4@neurahive.com",
                password="client4",
                agents=[],
            ),
            User(
                role=[3],
                name="Client user 5",
                email="client5@neurahive.com",
                password="client5",
                agents=[],
            ),
        ]

    def _populate_users(self, session: Session) -> None:
        if self._users:
            session.add_all(self._users)
            session.commit()

    def _initialize_knowledge_bases(self) -> None:
        self._knowledge_bases = [
            KnowledgeBase(
                name="Dados do setor de administração",
                data={},
            ),
            KnowledgeBase(name="Dados do setor de vendas", data={}),
            KnowledgeBase(name="Dados do setor do financeiro", data={}),
            KnowledgeBase(
                name="Dados do setor de TI",
                data={
                    "questions": [
                        "O que faço se meu computador travar?",
                        "Como acesso a rede Wi-Fi da empresa?",
                        "Perdi meu acesso ao sistema interno. E agora?",
                        "Como reportar um ataque de phishing?",
                        "Posso instalar programas no meu computador corporativo?",
                    ],
                    "answers": [
                        "Reinicie o computador. Se o problema persistir, envie um chamado pelo sistema de suporte."
                        "Use o nome da rede 'Empresa-WiFi' e a senha fornecida pelo TI no seu primeiro dia.",
                        "Entre em contato com suporte@empresa.com e solicite redefinição de senha.",
                        "Encaminhe o e-mail suspeito para ti@empresa.com e não clique em nenhum link.",
                        "Não. Qualquer instalação deve ser aprovada e feita pela equipe de TI.",
                    ],
                },
            ),
        ]

    def _populate_knowledge_bases(self, session: Session) -> None:
        if self._knowledge_bases:
            session.add_all(self._knowledge_bases)
            session.commit()

    def _initialize_agents(self) -> None:
        if self._knowledge_bases:
            self._agents = [
                Agent(
                    name="Agent 1",
                    users=[],
                    groups=[],
                    theme="Administração",
                    behavior="Responda de forma clara, útil e educada. Varie o estilo mantendo o sentido original. "
                    "Use uma linguagem acessível, mas mantenha profissionalismo.",
                    knowledge_base_id=self._knowledge_bases[0].id,
                ),
                Agent(
                    name="Agent 2",
                    users=[],
                    groups=[],
                    theme="Setor de vendas",
                    behavior="Responda de forma clara, útil e educada. Varie o estilo mantendo o sentido original. "
                    "Use uma linguagem acessível, mas mantenha profissionalismo.",
                    knowledge_base_id=self._knowledge_bases[1].id,
                ),
                Agent(
                    name="Agent 3",
                    users=[],
                    groups=[],
                    theme="Financeiro",
                    behavior="Responda de forma clara, útil e educada. Varie o estilo mantendo o sentido original. "
                    "Use uma linguagem acessível, mas mantenha profissionalismo.",
                    knowledge_base_id=self._knowledge_bases[2].id,
                ),
                Agent(
                    name="Agent 4",
                    users=[],
                    groups=[],
                    theme="TI",
                    behavior="Responda de forma clara, útil e educada. Varie o estilo mantendo o sentido original. "
                    "Use uma linguagem acessível, mas mantenha profissionalismo.",
                    knowledge_base_id=self._knowledge_bases[3].id,
                ),
            ]

    def _populate_agents(self, session: Session) -> None:
        if self._agents:
            session.add_all(self._agents)
            session.commit()

    def _initialize_chats(self) -> None:
        if self._users and self._agents:
            self._chats = [Chat(user_id=self._users[2].id, agent_id=self._agents[3].id)]

    def _populate_chats(self, session: Session) -> None:
        if self._chats:
            session.add_all(self._chats)
            session.commit()


if __name__ == "__main__":
    PopulateDatabase().execute()
