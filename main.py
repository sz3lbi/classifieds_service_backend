from app.core.logger import logger
from app.factory import create_app
from app.core.scheduler import arq_worker

app = create_app()


@app.on_event("startup")
async def startup_event():
    await arq_worker.start(handle_signals=False)


@app.on_event("shutdown")
async def shutdown_event():
    await arq_worker.close()


if __name__ == "__main__":
    import uvicorn

    app.logger = logger

    logger.info("Starting uvicorn in reload mode")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        reload=True,
        port=int("8000"),
    )
