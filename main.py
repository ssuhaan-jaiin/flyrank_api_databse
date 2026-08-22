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
    if not new_task.title.strip():
        return JSONResponse(status_code=400, content={"error": "Title is required"})

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (new_task.title, 0)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return JSONResponse(
        status_code=201,
        content={"id": new_id, "title": new_task.title, "done": False}
    )


@app.put("/tasks/{task_id}", summary="Update a task")
def update_task(task_id: int, updates: TaskUpdate):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        conn.close()
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    new_title = row["title"]
    new_done = row["done"]

    if updates.title is not None:
        if not updates.title.strip():
            conn.close()
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty"})
        new_title = updates.title

    if updates.done is not None:
        new_done = int(updates.done)

    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )
    conn.commit()
    conn.close()

    return {"id": task_id, "title": new_title, "done": bool(new_done)}


@app.delete("/tasks/{task_id}", summary="Delete a task")
def delete_task(task_id: int):
    conn = get_connection()
    row = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()

    if row is None:
        conn.close()
        return JSONResponse(status_code=404, content={"error": "Task not found"})

    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

    return JSONResponse(status_code=204, content=None)