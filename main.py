from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from database import init_db

init_db()

app = FastAPI()


tasks = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Walk the dog", "done": False},
    {"id": 3, "title": "Write the report", "done": True},
]

# shape required for creating a task 
class TaskCreate(BaseModel):
    title: str

# shape required for updating a task
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    done: Optional[bool] = None


@app.get("/", summary="API info")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def get_tasks():
    # returns the whole list, no filtering
    return tasks


@app.get("/tasks/{task_id}", summary="Get a single task")
def get_task(task_id: int):
    # task_id comes from the URL, auto-converted to int
    for task in tasks:
        if task["id"] == task_id:
            return task  # 200 by default
    # no match found in the loop
    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.post("/tasks", summary="Create a task")
def create_task(new_task: TaskCreate):
    # new_task is parsed from the request body automatically
    if not new_task.title.strip():
        # empty or whitespace-only title is rejected
        return JSONResponse(status_code=400, content={"error": "Title is required"})

    # next free id = current highest id + 1 (0 if list is empty)
    next_id = max((task["id"] for task in tasks), default=0) + 1
    task = {"id": next_id, "title": new_task.title, "done": False}
    tasks.append(task)  # mutate the in-memory list
    return JSONResponse(status_code=201, content=task)


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, updates: TaskUpdate):
    for task in tasks:
        if task["id"] == task_id:
            if updates.title is not None:
                # client wants to change the title
                if not updates.title.strip():
                    return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
                task["title"] = updates.title

            if updates.done is not None:
                # client wants to change the done flag
                task["done"] = updates.done

            return task  # 200 by default, updated task

    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})


@app.delete("/tasks/{task_id}", summary="Delete a task")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)  # actually remove it from the list
            return JSONResponse(status_code=204, content=None)  # success, empty body

    return JSONResponse(status_code=404, content={"error": f"Task {task_id} not found"})