from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    ARRAY,
    Column,
    ForeignKey,
    Boolean,
    DateTime,
    Integer,
    String,
    Table,
    func,
    select,
    text,
    Float,
    JSON,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    declarative_base,
    relationship,
    Session,
)

Base = declarative_base()


class Example(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_onupdate=func.now())


group_agent_association = Table(
    "group_agent",
    Base.metadata,
    Column("group_id", Integer, ForeignKey("group.id"), primary_key=True),
    Column("agent_id", Integer, ForeignKey("agent.id"), primary_key=True),
)

user_agent_association = Table(
    "user_agent",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("agent_id", Integer, ForeignKey("agent.id"), primary_key=True),
)


class User(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    agents = relationship(
        "Agent",
        secondary=user_agent_association,
        back_populates="users",
        cascade="all, delete",
        lazy="joined",
    )


class Agent(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String)
    theme: Mapped[str] = mapped_column(String)
    behavior: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    temperature: Mapped[float] = mapped_column(Float, default=0.5)
    top_p: Mapped[float] = mapped_column(Float, default=0.5)
    knowledge_base_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("knowledge_base.id"), unique=True, nullable=True
    )
    image_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    users = relationship(
        "User",
        secondary=user_agent_association,
        back_populates="agents",
        cascade="all, delete",
        lazy="joined",
    )

    groups = relationship(
        "Group",
        secondary=group_agent_association,
        back_populates="agents",
        cascade="all, delete",
        lazy="joined",
    )


class Group(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    agents = relationship(
        "Agent",
        secondary=group_agent_association,
        back_populates="groups",
        cascade="all, delete",
        lazy="joined",
    )


class Chat(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "chat"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    agent_id: Mapped[int] = mapped_column(ForeignKey("agent.id"))
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    @staticmethod
    def get_chat_by_id(session: Session, chat_id: int) -> Chat | None:  # noqa: F821
        query = select(Chat).where(Chat.id == chat_id)
        result = session.execute(query)
        return result.scalars().first()


class ChatHistory(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "chat_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chat.id"))
    message: Mapped[str] = mapped_column(String)
    is_user_message: Mapped[bool] = mapped_column(Boolean)
    message_date: Mapped[datetime] = mapped_column(DateTime)

    @staticmethod
    def add_chat_history(
        session: Session,
        chat_id: int,
        message: str,
        is_user_message: bool,
        message_date: datetime,
    ) -> None:
        chat_history = ChatHistory(
            chat_id=chat_id,
            message=message,
            is_user_message=is_user_message,
            message_date=message_date,
        )
        session.add(chat_history)
        session.commit()


class KnowledgeBase(Base):  # type: ignore[valid-type, misc]
    __tablename__ = "knowledge_base"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    data: Mapped[str] = mapped_column(JSON, nullable=False)
