# HiveSync Backend Specification  
Version: 1.0  
Language: Python 3.11  
Framework: FastAPI  
Architecture: Modular Service Layer (app/api, app/services, app/models, app/workers)  
Status: Ready for Production Build

---

# 1. Overview

The HiveSync backend is a FastAPI-based service providing:

- User authentication
- Project metadata management
- AI documentation orchestration
- Preview bundle creation
- Object storage integration for preview delivery
- Background job queue processing
- GPU/CPU worker autoscaling (optional)
- Cross-client communication for desktop/mobile/iPad
- Plugin API surface (VS Code, JetBrains, etc.)

The backend is fully Dockerized, designed for local development and scalable production environments.

---

# 2. Architecture

```
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   ├── utils/
│   ├── workers/
│   └── main.py
├── tests/
├── Dockerfile
├── docker-compose.yml
├── backend.env.example
└── requirements.txt
```

## 2.1 Key Principles
- Modular service layer (auth, preview_builder, ai_engine, etc.)
- Stateless JWT authentication
- Stateless preview tokens
- Redis-backed queueing
- Postgres persistence
- S3/R2-compatible storage abstraction
- Optional GPU workers for AI tasks
- Full separation between API and worker logic

---

# 3. Core Technologies

- **FastAPI** (API framework)
- **Uvicorn / Gunicorn** (ASGI server)
- **SQLModel / SQLAlchemy** (ORM)
- **PostgreSQL** (database)
- **Redis** (cache, rate limiting, queues)
- **Celery or RQ** (queueing, worker orchestration)
- **Pydantic** (schemas)
- **Boto3 or Minio SDK** (object storage)
- **Python-JOSE** (JWT)
- **HTTPX** (upstream API calls—OpenAI, etc.)

---

# 4. API Layout

```
app/api/v1/
├── users.py
├── projects.py
├── preview.py
└── __init__.py
```

Full endpoint details are contained in `api_endpoints.md`.

---

# 5. Configuration System

Located in:  
`backend/app/core/config.py`

## 5.1 ENV Variables
Automatically loaded from:
- Environment
- `.env` file
- Docker secrets (if applicable)

### Primary Variables
- PORT  
- BASE_URL
- JWT_SECRET  
- POSTGRES_*  
- REDIS_*  
- EMAIL_PROVIDER  
- RESEND_API_KEY  
- OPENAI_API_KEY  
- LOCAL_AI_MODEL_PATH  
- LOCAL_AI_ENABLED  
- PREVIEW_MAX_TIMEOUT_MS  
- LOG_LEVEL  
- R2_ENDPOINT  
- R2_BUCKET  
- R2_ACCESS_KEY  
- R2_SECRET_KEY  

All are defined in `backend.env.example`.

---

# 6. Data Models

All models use SQLModel.

## 6.1 User Model (SQLModel)
Fields:
- id: int (PK)  
- email: str, unique  
- username: str, unique  
- password_hash: str  
- created_at: datetime  
- last_login: datetime  
- preferences: JSON  

## 6.2 Project Model
Fields:
- id  
- owner_id (FK → User.id)  
- name  
- created_at  
- updated_at  
- config (JSON)  

## 6.3 AIRequest Model
Used for logging worker jobs.

Fields:
- id  
- project_id  
- user_id  
- file_path  
- input_text  
- output_text  
- created_at  
- completed_at  

## 6.4 Preview Log Model
Stores previews for analytics (not tokens).

Fields:
- id  
- project_id  
- user_id  
- timestamp  
- bundle_size  
- storage_url  

---

# 7. Schemas

Located in `app/schemas/`.

## 7.1 User Schemas
- UserCreate  
- UserLogin  
- UserRead  
- UserUpdate  

## 7.2 Project Schemas
- ProjectCreate  
- ProjectRead  
- ProjectUpdate  

## 7.3 Preview Schemas
- PreviewRequest  
- PreviewResponse  
- PreviewTokenSchema  

---

# 8. Services Layer

Located in `app/services/`.

## 8.1 Authentication Service
Handles:
- password hashing  
- JWT issuing  
- JWT validation  
- login rate limiting  

## 8.2 User Service
Handles:
- registration  
- login  
- update profile  
- preference saving  
- searching users for share-preview flow  

## 8.3 Project Service
Responsible for:
- create project  
- update project  
- list user projects  
- metadata  
- retrieving file structure (future)  

## 8.4 Preview Builder Service
**Core component of HiveSync.**

Responsibilities:
- Accept request from desktop/IDE to build preview  
- Trigger bundling process  
- Enforce timeout window  
- Upload result to R2/S3  
- Return signed URL + stateless token  

Preview build steps:
1. Receive request  
2. Validate user permissions  
3. Create temporary build directory  
4. Run bundler (Metro/Expo CLI)  
5. Minify + compress  
6. Upload bundle + assets to storage  
7. Generate signed URL (10-minute expiry)  
8. Generate preview token  
9. Return response to client  

Failure handling:
- Timeout  
- Build error  
- Upload failed  
- Storage unreachable  

## 8.5 AI Engine Service
Provides unified interface for:
- OpenAI  
- Local model  
- Failover logic  

Handles:
- file summaries  
- inline comments  
- rename suggestions  
- docstring generation  
- full-file documentation passes  

## 8.6 Storage Service
Abstracted API for:
- R2  
- S3  
- MinIO  

Functions:
- upload_file  
- get_signed_url  
- delete_file  

## 8.7 Autoscaler Service (Optional)
Controls:
- GPU worker spin-up  
- worker scale-down  
- queue pressure detection  
- cooldown period  
- health checks  

---

# 9. Utils

Utilities stored in:

```
app/utils/
├── tokens.py
├── crypto.py
└── time.py
```

## 9.1 Token Utility
Generates/validates:
- JWTs  
- preview tokens  

## 9.2 Crypto Utility
Wraps:
- bcrypt hashing  
- random hex generation  
- secure compare  

## 9.3 Time Utility
Provides:
- timestamp helpers  
- expiration validation  
- timezone normalization  

---

# 10. Worker System

Workers handle background jobs for previews and AI tasks.

```
app/workers/
├── queues.py
├── cpu_worker.py
└── gpu_worker.py
```

## 10.1 Queues
Two Redis queues:
- `cpu_tasks`
- `gpu_tasks`

## 10.2 CPU Worker
Handles:
- lightweight AI tasks  
- metadata operations  
- file scanning  
- notifications  

## 10.3 GPU Worker
Handles:
- large AI inference  
- local model inference  
- summarization at scale  

## 10.4 Autoscaler Logic
Triggered when:
- queue_length > threshold  
- average wait time increases  
- GPU idle < threshold  

Scaling rules defined in Deployment Bible.

---

# 11. Authentication

## 11.1 Register
- Validates unique email + username  
- Hashes password  
- Saves user  
- Returns JWT  

## 11.2 Login
- Validates credentials  
- Returns JWT  
- Rate limited  

## 11.3 JWT
Payload:
- user_id  
- expires  
- roles  

Algorithm: HS256

---

# 12. Project Management

Basic CRUD:
- create  
- read  
- update  

Future:
- import from GitHub  
- multiple contributors  

---

# 13. Preview System (Backend)

The most important backend feature.

## 13.1 Endpoint (`POST /preview/build`)
Request:
- project_id  
- target_platform (ios/android)  
- entry_file  
- environment  

Backend steps:
1. Authenticate user  
2. Verify project ownership  
3. Create temp working directory  
4. Write source files  
5. Run bundler  
6. Package bundle  
7. Upload  
8. Generate token  
9. Build response JSON  

## 13.2 Stateless Token
Contains:
- project_id  
- expiration  
- signature  

## 13.3 Storage Upload
Files uploaded:
- bundle.js  
- assets/  
- metadata.json  

## 13.4 Response
```
{
  "url": "...signed_url...",
  "token": "...",
  "expires_in": 600
}
```

---

# 14. AI Documentation System

## 14.1 Workflow
1. Client requests doc generation  
2. Backend enqueues job  
3. Worker processes job  
4. Worker returns result  
5. Backend stores result  
6. Client receives notification  

## 14.2 Job Types
- inline_comment  
- file_summary  
- function_doc  
- variable_rename  
- full_file_pass  

## 14.3 Local Model Integration
Enabled via:
```
LOCAL_AI_ENABLED=true
LOCAL_AI_MODEL_PATH=/models/deepseek
```

Backend loads:
- tokenizer  
- model weights  

Fallbacks:
- Local → OpenAI primary → OpenAI secondary

---

# 15. Notifications

Backend pushes:
- Documentation completed  
- Preview ready  
- Error alerts  

Transport:
- Polling from clients  
- WebSockets (future)  

---

# 16. Error Handling

## 16.1 Response Format
```
{
  "error": {
    "code": "PREVIEW_TIMEOUT",
    "message": "Preview bundle timed out",
    "details": {...}
  }
}
```

## 16.2 Categories
- AUTH_ERROR  
- RATE_LIMIT  
- PREVIEW_ERROR  
- AI_ERROR  
- STORAGE_ERROR  
- INTERNAL_ERROR  

---

# 17. Logging

Logs include:
- timestamp  
- level  
- service  
- request_id  
- user_id (when applicable)  
- message  

Stored locally and optionally forwarded.

---

# 18. Health Checks

## 18.1 Built-In API
- `/health`  
- `/health/db`  
- `/health/redis`  

## 18.2 Python Health Script (detailed)
- redis availability  
- postgres availability  
- queue sizes  
- worker responsiveness  
- autoscaler state  

---

# 19. Deployment Details

Full instructions in deployment_bible.md.

## 19.1 Containerized System
Services:
- backend  
- workers  
- redis  
- postgres  

## 19.2 Scaling
- Horizontal scaling allowed  
- Stateless API  
- Workers scale independently  

---

# 20. Cross-Client Integration

Backend supports:
- desktop app  
- iPad app  
- mobile preview app  
- IDE plugins  

All communicate through the same API.

---

# 21. End of Backend Spec

This file defines **all backend behavior** and is binding for build phases.

