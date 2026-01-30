from fastapi import FastAPI
from .api.run import router as run_router
from .api.prompts import router as prompts_router
from .api.memory import router as memory_router

app = FastAPI(title="Design-Aware AI Coding Platform")

app.include_router(run_router)
app.include_router(prompts_router)
app.include_router(memory_router)


@app.get("/")
def health():
    return {"status": "ok"}
