from fastapi import FastAPI
from database import Base, engine

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get('/')
async def root():
    return {'message': 'FastAPI TodoList API'}
