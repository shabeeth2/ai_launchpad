from fastapi import FastAPI

app = FastAPI(title="Launchpad", version="0.1.0")

# app.include_router(workflow.router, prefix="/api/v1", tags=["Workflow"])

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/chat_stream/{message}")
async def chat_stream(message: str, checkpoint_id: Optional[str] = Query(None)):
    return StreamingResponse(
        generate_chat_responses(message, checkpoint_id), 
        media_type="text/event-stream"
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
