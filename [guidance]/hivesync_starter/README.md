
# HiveSync Starter Backend

This is a minimal FastAPI-based starter project intended as a foundation for the HiveSync doc/sync admin backend.

## Features

- FastAPI application with basic structure
- SQLite database via SQLAlchemy
- Simple User model with admin flag
- Basic auth + admin router stubs
- Health check endpoint
- Admin bootstrap script to create the first admin user

This is **not** the full HiveSync spec yet, but a solid starting point you can run immediately and extend.

## Quick start

### 1. Create a virtual environment

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Initialize the database & create admin user

```bash
python admin_bootstrap.py
```

Follow the prompts to create the first admin user.

### 4. Run the server

```bash
uvicorn app.main:app --reload
```

The API will be available at http://127.0.0.1:8000

- Docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health
