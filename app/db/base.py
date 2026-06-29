"""
SQLAlchemy Declarative Base.
모든 모델(app/models/*.py)은 이 Base를 상속한다.
"""
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
