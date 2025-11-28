from datetime import datetime
from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from database import Base, Todo, engine, get_db

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Create API router with /api prefix
router = APIRouter(prefix='/api')


# Pydantic model for Todo response
class TodoModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 way

    id: int
    title: str
    description: str | None
    completed: bool
    created_at: datetime
    updated_at: datetime


class TodoCreateModel(BaseModel):
    title: str
    description: str | None = None


class TodoUpdateModel(BaseModel):
    title: str | None = None
    description: str | None = None
    completed: bool | None = None


# Helper function to get todo by ID
def get_todo_by_id(todo_id: int, db: Session) -> Todo:
    """Get todo by ID, raise 404 if not found"""
    todo = db.get(Todo, todo_id)
    if not todo:
        raise HTTPException(status_code=404, detail='Todo not found')
    return todo


@router.get('/')
async def root():
    return {'message': 'FastAPI TodoList API'}


@router.get('/todos', response_model=list[TodoModel])
async def get_todos(db: Session = Depends(get_db)):
    todos = db.query(Todo).all()
    return todos


@router.post('/todos', status_code=status.HTTP_201_CREATED, response_model=TodoModel)
async def create_todo(todo: TodoCreateModel, db: Session = Depends(get_db)):
    try:
        new_todo = Todo(title=todo.title, description=todo.description)
        db.add(new_todo)
        db.commit()
        db.refresh(new_todo)  # Refresh to get database-generated fields (id, timestamps)
        return new_todo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to create todo: {str(e)}')


@router.get('/todos/{todo_id}', response_model=TodoModel)
async def get_todo(todo_id: int, db: Session = Depends(get_db)):
    existing_todo = get_todo_by_id(todo_id, db)
    return existing_todo


@router.put('/todos/{todo_id}', response_model=TodoModel)
async def update_todo(todo_id: int, todo: TodoUpdateModel, db: Session = Depends(get_db)):
    existing_todo = get_todo_by_id(todo_id, db)

    try:
        for field, value in todo.model_dump(exclude_unset=True).items():
            setattr(existing_todo, field, value)

        db.commit()
        db.refresh(existing_todo)
        return existing_todo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to update todo: {str(e)}')


@router.delete('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    existing_todo = get_todo_by_id(todo_id, db)

    try:
        db.delete(existing_todo)
        db.commit()
        return {'ok': True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Failed to delete todo: {str(e)}')


app.include_router(router)
