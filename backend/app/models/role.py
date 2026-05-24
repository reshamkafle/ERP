import enum

from sqlalchemy import Boolean, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RoleType(str, enum.Enum):
    SUPER_ADMIN = "SUPER_ADMIN"
    ADMIN = "ADMIN"
    DIRECTOR = "DIRECTOR"
    IT = "IT"
    EMPLOYEE = "EMPLOYEE"


class Department(str, enum.Enum):
    GENERAL = "general"
    ACCOUNTING = "accounting"
    WAREHOUSE = "warehouse"
    SALES = "sales"
    IT = "it"


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), unique=True)
    role_type: Mapped[RoleType] = mapped_column(Enum(RoleType, name="roletype"), nullable=False)
    department: Mapped[Department | None] = mapped_column(
        Enum(Department, name="department"),
        nullable=True,
    )
    is_system: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    description: Mapped[str | None] = mapped_column(String(512), nullable=True)

    permission_links: Mapped[list["RolePermission"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )
    user_links: Mapped[list["UserRoleAssignment"]] = relationship(
        back_populates="role",
        cascade="all, delete-orphan",
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        index=True,
    )

    role: Mapped["Role"] = relationship(back_populates="permission_links")
    permission: Mapped["Permission"] = relationship(back_populates="role_links")


class UserRoleAssignment(Base):
    __tablename__ = "user_role_assignments"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_user_role"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id", ondelete="CASCADE"), index=True)

    user: Mapped["User"] = relationship(back_populates="role_assignments")
    role: Mapped["Role"] = relationship(back_populates="user_links")


class UserPermissionOverride(Base):
    """Per-user grant or revoke on top of role-based permissions."""

    __tablename__ = "user_permission_overrides"
    __table_args__ = (
        UniqueConstraint("user_id", "permission_id", name="uq_user_permission_override"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    permission_id: Mapped[int] = mapped_column(
        ForeignKey("permissions.id", ondelete="CASCADE"),
        index=True,
    )
    granted: Mapped[bool] = mapped_column(Boolean, nullable=False)

    user: Mapped["User"] = relationship(back_populates="permission_overrides")
    permission: Mapped["Permission"] = relationship(back_populates="user_overrides")
