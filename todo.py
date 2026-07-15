from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional
app = FastAPI(
    title="Task API",
    description="A small API that manages a to-do list with full CRUD operations.",
    version="1.0"
)

tasks_db = [
    {"id": 1, "title": "Setup FastAPI project", "done": True},
    {"id": 2, "title": "Configure Git & GitHub", "done": True},
    {"id": 3, "title": "Complete CRUD assignment", "done": False}
]

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="The title of the task cannot be empty")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Updated title of the task")
    done: Optional[bool] = Field(None, description="Updated status of the task")


@app.get("/", status_code=status.HTTP_200_OK)
def read_root():
    """Returns the details of this To-Do API."""
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }

@app.get("/health", status_code=status.HTTP_200_OK)
def check_health():
    """Endpoint for monitoring tool to check if server is alive."""
    return {"status": "ok"}

@app.get("/tasks", status_code=status.HTTP_200_OK)
def get_all_tasks():
    """Returns the list of all tasks."""
    return tasks_db

@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def get_single_task(task_id: int):
    """Returns a single task by its ID. Returns 404 if not found."""
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task_input: TaskCreate):
    """Creates a new task with status 201."""
    new_id = max([task["id"] for task in tasks_db]) + 1 if tasks_db else 1
    
    new_task = {
        "id": new_id,
        "title": task_input.title,
        "done": False 
    }
    tasks_db.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
def update_task(task_id: int, task_input: TaskUpdate):
    """Replaces/Updates a task's title and/or done status."""
    for task in tasks_db:
        if task["id"] == task_id:
            if task_input.title is None and task_input.done is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Please provide 'title' or 'done' to update."
                )
            
            if task_input.title is not None:
                task["title"] = task_input.title
            if task_input.done is not None:
                task["done"] = task_input.done
            return task
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int):
    """Removes a task by its ID. Returns empty body with status 204."""
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(index)
            return None 
            
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {task_id} not found"
    )