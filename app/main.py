from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.db import engine, Base
from app.routers import students, routes, trips


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="UniBus Core API",
    description="Core microservice for UniBus platform - Manages students, routes, and trips",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(students.router)
app.include_router(routes.router)
app.include_router(trips.router)


@app.get("/", tags=["health"])
def health_check():
    return {"status": "ok", "message": "UniBus Core service is running."}


@app.get("/health", tags=["health"])
def health():
    return {"status": "healthy", "service": "unibus-core-api"}
