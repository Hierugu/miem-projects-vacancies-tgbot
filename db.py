from typing import List, Set, Optional
from dotenv import load_dotenv

from sqlalchemy import create_engine, Column, BigInteger, Text, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.dialects.postgresql import insert

import os

from logger import logger

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL') or (
    f"postgresql://{os.getenv('PGUSER','postgres')}:{os.getenv('PGPASSWORD','')}@{os.getenv('PGHOST','localhost')}:{os.getenv('PGPORT','5432')}/{os.getenv('PGDATABASE','vacancies_db')}"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Vacancy(Base):
    __tablename__ = 'known_vacancies'
    vacancy_id = Column(BigInteger, primary_key=True, index=True)
    added_at = Column(DateTime(timezone=True), server_default=func.now())


class UserFilter(Base):
    __tablename__ = 'user_filters'
    user_id = Column(BigInteger, primary_key=True, index=True)
    filter_text = Column(Text)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


def init_db():
    Base.metadata.create_all(bind=engine)
    logger.warning('Database initialized (SQLAlchemy tables created).')


def is_initialized() -> bool:
    try:
        with SessionLocal() as session:
            session.execute('SELECT 1')
        return True
    except Exception:
        return False


def add_user(user_id: int, username: Optional[str] = None):
    with SessionLocal() as session:
        stmt = insert(User).values(id=user_id, username=username).on_conflict_do_update(index_elements=[User.id], set_=dict(username=username))
        session.execute(stmt)
        session.commit()


def remove_user(user_id: int):
    with SessionLocal() as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()


def list_users() -> List[int]:
    with SessionLocal() as session:
        rows = session.query(User.id).all()
        return [int(r[0]) for r in rows]


def get_known_vacancy_ids() -> Set[str]:
    with SessionLocal() as session:
        rows = session.query(Vacancy.vacancy_id).all()
        return set(str(r[0]) for r in rows)


def add_vacancy_ids(vacancy_ids: List[int]):
    if not vacancy_ids:
        return
    with SessionLocal() as session:
        for vid in vacancy_ids:
            try:
                stmt = insert(Vacancy).values(vacancy_id=int(vid)).on_conflict_do_nothing(index_elements=[Vacancy.vacancy_id])
                session.execute(stmt)
            except Exception:
                continue
        session.commit()


def get_filter(user_id: int) -> Optional[str]:
    with SessionLocal() as session:
        uf = session.get(UserFilter, user_id)
        return uf.filter_text if uf else None


def set_filter(user_id: int, filter_text: str):
    with SessionLocal() as session:
        stmt = insert(UserFilter).values(user_id=user_id, filter_text=filter_text).on_conflict_do_update(index_elements=[UserFilter.user_id], set_=dict(filter_text=filter_text))
        session.execute(stmt)
        session.commit()
