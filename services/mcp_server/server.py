from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .schemas import ToolRequest, ToolResponse
from .tools.lint import run_lint
from .tools.test import run_test
from .tools.coverage import run_coverage

app = FastAPI(title="MCP Tool Server")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/tool/{name}", response_model=ToolResponse)
def run_tool(name: str, req: ToolRequest):
    if name == "lint":
        result = run_lint(req.payload)
    elif name == "test":
        result = run_test(req.payload)
    elif name == "coverage":
        result = run_coverage(req.payload)
    else:
        raise HTTPException(status_code=404, detail="Unknown tool")

    return ToolResponse(status=result["status"], detail=result["detail"])
