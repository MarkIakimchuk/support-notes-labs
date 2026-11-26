from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from app.posts import router as posts_router
from app.auth import router as auth_router
from app.users import router as users_router

app = FastAPI(title="База решений техподдержки")


@app.get("/")
def home():
    return {"message": "База решений техподдержки", "docs": "/docs"}


@app.get("/about")
def about():
    return {"name": "База решений техподдержки", "version": "1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}


app.include_router(posts_router)
app.include_router(users_router)
app.include_router(auth_router)


@app.get("/library", include_in_schema=False)
def library():
    return FileResponse(Path(__file__).parent / "static" / "library.html", media_type="text/html")
