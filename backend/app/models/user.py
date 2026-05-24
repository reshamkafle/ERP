import enum

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class UserRole(str, enum.Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    CASHIER = "CASHIER"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="userrole"), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    token_version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    sales: Mapped[list["Sale"]] = relationship(
        back_populates="created_by_user",
        foreign_keys="Sale.created_by_id",
    )
    purchases: Mapped[list["Purchase"]] = relationship(back_populates="created_by_user")
    procurement_runs: Mapped[list["ProcurementRun"]] = relationship(
        back_populates="created_by_user",
    )
    promotion_runs: Mapped[list["PromotionRun"]] = relationship(
        back_populates="created_by_user",
    )
    role_assignments: Mapped[list["UserRoleAssignment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    permission_overrides: Mapped[list["UserPermissionOverride"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
    preferences: Mapped["UserPreference | None"] = relationship(
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
