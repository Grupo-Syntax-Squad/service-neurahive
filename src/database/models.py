from datetime import datetime
from sqlalchemy import (
    ARRAY,
    ForeignKey,
    Boolean,
    DateTime,
    Integer,
    String,
    func,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

Base = declarative_base()


class Example(Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_onupdate=func.now())

class GroupAgent(Base):
    __tablename__ = "group_agent"

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('group.id'), primary_key=True)
    agent_id: Mapped[int] = mapped_column(Integer, ForeignKey('agent.id'), primary_key=True)

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    role: Mapped[list[int]] = mapped_column(ARRAY(Integer))
    name: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True, server_onupdate=func.now()
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

class Agent(Base):
    __tablename__ = "agent"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)

class Group(Base):
    __tablename__ = "group"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))

    agents = relationship('Agent', secondary=GroupAgent, back_populates='groups')