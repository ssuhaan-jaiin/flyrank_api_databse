from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional
from database import init_db, get_connection 

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


@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [{"id": row["id"], "title": row["title"], "done": bool(row["done"])} for row in rows]


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()

    if row is None:
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    return {"id": row["id"], "title": row["title"], "done": bool(row["done"])}


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