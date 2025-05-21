from datetime import datetime
from src.schemas.statistics import (
    GeneralStatisticsResponse,
    GeneralStatisticsRequest,
    UserInteractionsRequest,
    UserInteractionsResponse,
)
from src.schemas.basic_response import BasicResponse
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import HTTPException, status
from typing import Any


class GeneralStatistics:
    def __init__(self, session: Session, params: GeneralStatisticsRequest) -> None:
        self._session = session
        self._params = params
        self._statistics: dict[str, Any] = {}

    def execute(self) -> BasicResponse[GeneralStatisticsResponse]:
        try:
            self._get_statistics()
            if self._statistics is None:
                raise HTTPException(
                    detail="Erro ao buscar as estatísticas.",
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            return BasicResponse(
                data=GeneralStatisticsResponse(**self._statistics)
            )
        except Exception as e:
            raise HTTPException(
                detail=f"Erro ao buscar as estatísticas: {e}.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_statistics(self) -> None:
        query = text("""
            SELECT
                (SELECT COUNT(*) FROM agent) AS total_agents,
                (SELECT COUNT(*) FROM "user") AS total_users,
                COUNT(DISTINCT chat.id) AS total_conversations,
                COUNT(DISTINCT chat_history.id) AS total_messages,
                COUNT(DISTINCT CASE WHEN chat_history.message_date >= NOW() - INTERVAL '7 days' THEN agent.id END) AS total_agents_with_recent_iteractions,
                COUNT(DISTINCT CASE WHEN chat_history.message_date >= NOW() - INTERVAL '7 days' THEN "user".id END) AS total_users_with_recent_iteractions
            FROM
                agent
            LEFT JOIN
                chat ON chat.agent_id = agent.id
            LEFT JOIN
                "user" ON "user".id = chat.user_id
            LEFT JOIN
                chat_history ON chat_history.chat_id = chat.id
            WHERE
                (chat_history.message_date BETWEEN :start_date AND :end_date OR :start_date IS NULL OR :end_date IS NULL)
        """)
        params = {
            "start_date": self._params.start_date,
            "end_date": self._params.end_date,
        }
        result = self._session.execute(query, params).fetchone()
        if result is None:
            raise HTTPException(
                detail="Erro ao buscar as estatísticas.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        stats = dict(result._mapping)

        # Query para agente mais ativo
        query_active_agent = text("""
            SELECT
                agent.id AS most_active_agent_id,
                agent.name AS most_active_agent_name,
                COUNT(chat_history.id) AS total_messages
            FROM
                agent
            JOIN
                chat ON chat.agent_id = agent.id
            JOIN
                chat_history ON chat_history.chat_id = chat.id
            WHERE
                (chat_history.message_date BETWEEN :start_date AND :end_date OR :start_date IS NULL OR :end_date IS NULL)
            GROUP BY agent.id, agent.name
            ORDER BY total_messages DESC
            LIMIT 1
        """)
        active_agent = self._session.execute(query_active_agent, params).fetchone()
        if active_agent:
            stats["most_active_agent_id"] = active_agent.most_active_agent_id
            stats["most_active_agent_name"] = active_agent.most_active_agent_name
        else:
            stats["most_active_agent_id"] = 0
            stats["most_active_agent_name"] = ""

        self._statistics = stats


class UserInteractions:
    def __init__(self, session: Session, params: UserInteractionsRequest):
        self._session = session
        self._params = params

    def execute(self) -> list[UserInteractionsResponse]:
        if not self._params.user_id:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="O campo 'user_id' é obrigatório.",
            )

        end_date = self._params.end_date or datetime.utcnow().isoformat()
        start_date = self._params.start_date

        query = text("""
            SELECT
                u.id AS user_id,
                u.name AS user_name,
                COUNT(chh.id) AS user_iteractions,
                COUNT(DISTINCT a.id) AS iteractions_with_agents,
                MAX(chh.message_date) AS agent_last_iteraction
            FROM
                "user" u
            LEFT JOIN
                chat c ON c.user_id = u.id
            LEFT JOIN
                agent a ON a.id = c.agent_id
            LEFT JOIN
                chat_history chh ON chh.chat_id = c.id
            WHERE
                u.id = :user_id
                AND (:start_date IS NULL OR chh.message_date >= :start_date)
                AND (:end_date IS NULL OR chh.message_date <= :end_date)
                AND (:agent_id IS NULL OR a.id = :agent_id)
            GROUP BY u.id, u.name
        """)

        result = self._session.execute(query, {
            "user_id": self._params.user_id,
            "start_date": start_date,
            "end_date": end_date,
            "agent_id": self._params.agent_id,
        }).fetchall()

        response = [
            UserInteractionsResponse(
                user_id=row.user_id,
                user_name=row.user_name,
                user_iteractions=row.user_iteractions,
                iteractions_with_agents=row.iteractions_with_agents,
                agent_last_iteraction=row.agent_last_iteraction
            )
            for row in result
        ]

        return response