
from fastapi import FastAPI
from .db import Base, engine
from . import models
from .routers import health, admin

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="HiveSync Starter")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(admin.router, prefix="/admin", tags=["admin"])
