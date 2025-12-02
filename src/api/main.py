from fastapi import FastAPI
from src.api import workflow

app = FastAPI(title="LaunchPad", version="0.1.0")

app.include_router(workflow.router, prefix="/api", tags=["Workflow"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
