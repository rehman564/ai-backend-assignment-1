import os
import time
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# .env file se database ka link load karne ke liye
load_dotenv()

app = FastAPI(
    title="Task API with Postgres",
    description="A To-Do list API connected to a live PostgreSQL Database.",
    version="2.0"
)

DATABASE_URL = os.getenv("DATABASE_URL")

# Database Connection Helper Function
def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            # RealDictCursor se data dictionary format (JSON) mein milta hai
            conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
            return conn
        except psycopg2.OperationalError as e:
            print("Database not ready yet, retrying in 2 seconds...")
            time.sleep(2)
            retries -= 1
    raise Exception("Could not connect to PostgreSQL Database")

# ---- REQUEST BODY SCHEMAS ----
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title cannot be empty")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Updated title")
    done: Optional[bool] = Field(None, description="Updated done status")


# STAGE 1: Root & Health Endpoints
@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    return {"name": "Task API", "version": "2.0", "storage": "PostgreSQL"}

@app.get("/health", status_code=status.HTTP_200_OK)
def check_health():
    try:
        conn = get_db_connection()
        conn.close()
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=500, detail="Database connection failed")


# STAGE 2: Read Endpoints (GET)
@app.get("/tasks", status_code=status.HTTP_200_OK)
def get_all_tasks():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks ORDER BY id ASC;")
    tasks = cur.fetchall()
    cur.close()
    conn.close()
    return tasks

@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def get_single_task(task_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
    task = cur.fetchone()
    cur.close()
    conn.close()
    
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return task


# STAGE 3: Create Endpoint (POST)
@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_input: TaskCreate):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING *;",
        (task_input.title, False)
    )
    new_task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    return new_task


# STAGE 4: Update & Delete Endpoints (PUT & DELETE)
@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_input: TaskUpdate):
    if task_input.title is None and task_input.done is None:
        raise HTTPException(status_code=400, detail="Please provide 'title' or 'done' to update.")
        
    conn = get_db_connection()
    cur = conn.cursor()
    
    if task_input.title is not None and task_input.done is not None:
        cur.execute("UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING *;", (task_input.title, task_input.done, task_id))
    elif task_input.title is not None:
        cur.execute("UPDATE tasks SET title = %s WHERE id = %s RETURNING *;", (task_input.title, task_id))
    elif task_input.done is not None:
        cur.execute("UPDATE tasks SET done = %s WHERE id = %s RETURNING *;", (task_input.done, task_id))
        
    updated_task = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    if not updated_task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return updated_task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s RETURNING id;", (task_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return None