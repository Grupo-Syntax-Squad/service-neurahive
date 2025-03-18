from datetime import datetime
from enum import Enum
from sqlalchemy import Boolean, DateTime, Integer, String, Column, ForeignKey, func, text, Enum as SQLAlchemyEnum
from sqlalchemy.orm import Mapped, mapped_column, declarative_base, relationship

Base = declarative_base()


class Example(Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, server_default=text("TRUE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_onupdate=func.now())

class user_role(Base):
    __tablename__ = "user_role"
    user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
    role_id = Column(Integer, ForeignKey('role.id'), primary_key=True)

class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    modified_at: Mapped[datetime] = mapped_column(DateTime, server_onupdate=func.now())
    # last_login: Mapped[datetime] = mapped_column(DateTime)

    roles = relationship("Role", secondary="user_role", back_populates="users")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

class RoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"
    CURATOR = "curator"

class Role(Base):
    __tablename__ = "role"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[RoleEnum] = mapped_column(SQLAlchemyEnum(RoleEnum), nullable=False)

    def __repr__(self):
        return f"<Role(id={self.id}, name={self.name})>"
    
