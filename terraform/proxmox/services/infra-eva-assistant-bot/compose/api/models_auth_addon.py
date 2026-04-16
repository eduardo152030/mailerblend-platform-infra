# Añadir a models.py cuando se active el módulo auth
# (copiar estas clases al final de models.py)

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, Text, JSON, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class EVAUser(Base):
    """
    Usuarios de la UI de EVA (separado de User que es para Telegram).
    Tabla: eva_users
    """
    __tablename__ = "eva_users"

    id:            Mapped[int]      = mapped_column(primary_key=True)
    username:      Mapped[str]      = mapped_column(Text, unique=True, nullable=False)
    password_hash: Mapped[str]      = mapped_column(Text, nullable=False)
    display_name:  Mapped[str|None] = mapped_column(Text, nullable=True)
    is_active:     Mapped[bool]     = mapped_column(Boolean, nullable=False, default=True)
    created_at:    Mapped[str]      = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    permissions = relationship("UserPermission", back_populates="user", cascade="all, delete-orphan")


class UserPermission(Base):
    """
    Permisos por área para usuarios de la UI.
    Áreas: 'tareas' | 'contenido'
    Tabla: user_permissions
    """
    __tablename__ = "user_permissions"

    id:         Mapped[int]  = mapped_column(primary_key=True)
    user_id:    Mapped[int]  = mapped_column(ForeignKey("eva_users.id", ondelete="CASCADE"), nullable=False)
    area:       Mapped[str]  = mapped_column(Text, nullable=False)  # 'tareas' | 'contenido'
    can_read:   Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    can_write:  Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    can_delete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user = relationship("EVAUser", back_populates="permissions")
