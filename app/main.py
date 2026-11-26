from fastapi import FastAPI

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
