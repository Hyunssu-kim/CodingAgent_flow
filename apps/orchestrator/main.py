from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .api.run import router as run_router
from .api.prompts import router as prompts_router
from .api.memory import router as memory_router

app = FastAPI(title="Design-Aware AI Coding Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(run_router)
app.include_router(prompts_router)
app.include_router(memory_router)

ui_dir = Path(__file__).resolve().parents[1] / "ui"
if ui_dir.exists():
    app.mount("/ui", StaticFiles(directory=str(ui_dir), html=True), name="ui")


@app.get("/")
def health():
    return {"status": "ok"}
