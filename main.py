from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import init_db
from .routers import auth, users, skills, projects, resumes, recommendations, roadmap, interviews, events

app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to settings.frontend_origin in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/api/health")
def health():
    return {"status": "ok", "app": settings.app_name}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(skills.router)
app.include_router(projects.router)
app.include_router(resumes.router)
app.include_router(recommendations.router)
app.include_router(roadmap.router)
app.include_router(interviews.router)
app.include_router(events.router)
