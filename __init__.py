# app/api/__init__.py

from fastapi import FastAPI
from app.api.routes import router as api_router
from app.utils.logger import setup_logger
from app.config import load_config

config = load_config()
logger = setup_logger(config, 'api_logger')

app = FastAPI(title="Crypto Price Prediction API")

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("API Server is starting up.")
    # Additional startup tasks can be added here

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("API Server is shutting down.")
    await app.router.app.collector.close_exchanges()
    # Additional shutdown tasks can be added here
