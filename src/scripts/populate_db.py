from sqlalchemy import text
from src.database.get_db import get_db
from src.database.models import Agent, User


class PopulateDatabase:
    def __init__(self) -> None:
        self._session = get_db()
        self._users: list[User] | None = None
        self._agents: list[Agent] | None = None

    def execute(self) -> None:
        self._truncate_all_tables()

        self._initialize_users()
        self._populate_users()

        self._initialize_agents()
        self._populate_agents()

    def _truncate_all_tables(self) -> None:
        with self._session as session:
            session.execute(
                text('TRUNCATE TABLE agent, "user" RESTART IDENTITY CASCADE;')
            )
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
                name="Client user",
                email="client@neurahive.com",
                password="client",
                agents=[],
            ),
        ]

    def _populate_users(self) -> None:
        if self._users:
            with self._session as session:
                session.add_all(self._users)
                session.commit()

    def _initialize_agents(self) -> None:
        self._agents = [
            Agent(name="Agent 1", users=[], groups=[]),
            Agent(name="Agent 2", users=[], groups=[]),
            Agent(name="Agent 3", users=[], groups=[]),
            Agent(name="Agent 4", users=[], groups=[]),
        ]

    def _populate_agents(self) -> None:
        if self._agents:
            with self._session as session:
                session.add_all(self._agents)
                session.commit()


if __name__ == "__main__":
    PopulateDatabase().execute()
