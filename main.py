from contextlib import asynccontextmanager
from datetime import datetime
import os
from typing import Annotated
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Query, status
from sqlmodel import Field, SQLModel, Session, create_engine, select


# PostgreSQL connection URL format: postgresql+psycopg2://user:password@host:port/dbname
database_url = os.getenv('DATABASE_URL', 'postgresql+psycopg2://xlsama@localhost:5432/todolist')


engine = create_engine(database_url)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)

# Create API router with /api prefix
router = APIRouter(prefix='/api')


class Todo(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: str | None = Field(default=None)
    completed: bool = Field(default=False)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TodoCreate(SQLModel):
    title: str
    description: str | None = None


class TodoUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


@router.post('/todos', response_model=Todo, status_code=status.HTTP_201_CREATED)
async def create_todo(todo: TodoCreate, session: SessionDep):
    db_todo = Todo(**todo.model_dump())
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.get('/todos', response_model=list[Todo])
async def get_todos(
    session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100
):
    todos = session.exec(select(Todo).offset(offset).limit(limit)).all()
    return todos


@router.get('/todos/{todo_id}', response_model=Todo)
async def get_todo(todo_id: int, session: SessionDep):
    todo = session.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail='Todo not found')
    return todo


@router.patch('/todos/{todo_id}', response_model=Todo)
async def update_todo(todo_id: int, todo: TodoUpdate, session: SessionDep):
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail='Todo not found')
    todo_data = todo.model_dump(exclude_unset=True)
    db_todo.sqlmodel_update(todo_data)
    db_todo.updated_at = datetime.now()
    session.add(db_todo)
    session.commit()
    session.refresh(db_todo)
    return db_todo


@router.delete('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, session: SessionDep):
    db_todo = session.get(Todo, todo_id)
    if not db_todo:
        raise HTTPException(status_code=404, detail='Todo not found')
    session.delete(db_todo)
    session.commit()
    return {'ok': True}


app.include_router(router)
