from sqlalchemy import Column, ForeignKey, Table, create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    Session,
    mapped_column,
    relationship,
)

engine = create_engine("sqlite://")


class Base(DeclarativeBase):
    __abstract__ = True


group_role_association = Table(
    "group_role_association",
    Base.metadata,
    Column("group_id", ForeignKey("groups.id"), primary_key=True),  # type: ignore[arg-type]
    Column("role_id", ForeignKey("roles.id"), primary_key=True),  # type: ignore[arg-type]
)

user_roles_association = Table(
    "user_roles_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),  # type: ignore[arg-type]
    Column("role_id", ForeignKey("roles.id"), primary_key=True),  # type: ignore[arg-type]
)

user_group_association = Table(
    "user_group_association",
    Base.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),  # type: ignore[arg-type]
    Column("group_id", ForeignKey("groups.id"), primary_key=True),  # type: ignore[arg-type]
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(index=True)
    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary=user_group_association,
        back_populates="users",
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=user_roles_association,
        back_populates="users",
    )


class Role(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_roles_association,
        back_populates="roles",
    )

    groups: Mapped[list["Group"]] = relationship(
        "Group",
        secondary=group_role_association,
        back_populates="roles",
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(nullable=False)

    users: Mapped[list["User"]] = relationship(
        "User",
        secondary=user_group_association,
        back_populates="groups",
    )

    roles: Mapped[list["Role"]] = relationship(
        "Role",
        secondary=group_role_association,
        back_populates="groups",
    )


Base.metadata.create_all(engine)

session = Session(engine)
