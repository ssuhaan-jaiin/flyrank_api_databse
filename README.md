# Task API

A small CRUD API for managing a to-do list, built with FastAPI as part of the FlyRank Internship Backend track. Originally built with in-memory storage (W2 · A1), now backed by a real SQLite database (W3 · A2).

## Install & run

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The API runs at `http://localhost:8000`. Interactive docs (Swagger UI) at `http://localhost:8000/docs`.

The database file (`tasks.db`) is created automatically the first time the app runs, with 3 example tasks seeded in. It's git-ignored, so a fresh clone starts with no database — one gets built the moment you start the server.

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | / | API info |
| GET | /health | Health check |
| GET | /tasks | List all tasks |
| GET | /tasks/{task_id} | Get a single task |
| POST | /tasks | Create a task |
| PUT | /tasks/{task_id} | Update a task |
| DELETE | /tasks/{task_id} | Delete a task |

## Example request

```bash
curl -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d '{"title":"Buy milk"}'
```

```
HTTP/1.1 201 Created
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Database

Tasks are stored in a SQLite database instead of an in-memory list.

**Why SQLite:** it's a single file with no separate server to install or run — data survives a server restart, unlike the in-memory version this project started as.

**Where it lives:** `tasks.db`, in the project root. Created automatically on first run.

## Exploring the database directly

Opened `tasks.db` in [DB Browser for SQLite](https://sqlitebrowser.org) to run SQL by hand. Example query run in the "Execute SQL" tab:

```sql
UPDATE tasks SET done = 1;
```

This marks every row as done at once, since it has no `WHERE` clause — a direct demonstration of why the API's own update always includes `WHERE id = ?`. Running `GET /tasks` immediately afterward, with no restart, showed every task with `done: true` — proof that the API and DB Browser read the exact same file live.