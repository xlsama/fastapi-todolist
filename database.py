from datetime import datetime
import os
from sqlalchemy import Boolean, DateTime, Integer, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# PostgreSQL connection URL format: postgresql+psycopg2://user:password@host:port/dbname
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql+psycopg2://xlsama@localhost:5432/todolist')


# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    # Connection pool settings
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # 自动检测连接是否有效
    echo=False,  # 开发时可以设为 True 查看 SQL 语句
)


# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Create Base class for models
class Base(DeclarativeBase):
    pass


class Todo(Base):
    __tablename__ = 'todos'
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now
    )


# Dependency to get database session
def get_db():
    """
    Dependency function to get database session.
    Use this in FastAPI route handlers.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
