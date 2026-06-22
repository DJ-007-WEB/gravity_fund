from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.
    It contains the metadata registry that maps Python classes to database tables.
    """
    pass
