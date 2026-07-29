"""Declarative base configuration for SQLAlchemy 2.0 ORM."""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Common metadata configuration for all schema entities."""
    pass
