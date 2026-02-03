"""Main FastAPI application."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers import search, upload
from app.services.elasticsearch_service import ElasticsearchService
from app.services.mongodb_service import MongoDBService
from app.services.ollama_service import OllamaService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize services
mongodb_service = MongoDBService()
elasticsearch_service = ElasticsearchService()
ollama_service = OllamaService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    logger.info("Starting up Vouch application...")

    try:
        # Connect to MongoDB
        logger.info("Connecting to MongoDB...")
        await mongodb_service.connect()
        logger.info("MongoDB connected successfully")

        # Connect to Elasticsearch
        logger.info("Connecting to Elasticsearch...")
        await elasticsearch_service.connect()
        logger.info("Elasticsearch connected successfully")

        # Create Elasticsearch index if not exists
        logger.info("Creating Elasticsearch index...")
        await elasticsearch_service.create_index()
        logger.info("Elasticsearch index ready")

        # Set services in routers
        upload.set_services(mongodb_service, elasticsearch_service, ollama_service)
        search.set_services(mongodb_service, elasticsearch_service)

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}", exc_info=True)
        raise

    yield

    # Shutdown
    logger.info("Shutting down Vouch application...")
    await mongodb_service.disconnect()
    await elasticsearch_service.disconnect()
    logger.info("All services disconnected")


# Create FastAPI app
app = FastAPI(
    title="Vouch - Receipt Analysis",
    description="Upload and analyze receipts with AI-powered extraction and search",
    version="0.1.0",
    lifespan=lifespan
)

# Setup templates
templates_dir = Path(__file__).parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(upload.router)
app.include_router(search.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve main application page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    health_status = {
        "status": "healthy",
        "services": {}
    }

    # Check MongoDB
    try:
        mongodb_healthy = await mongodb_service.health_check()
        health_status["services"]["mongodb"] = "healthy" if mongodb_healthy else "unhealthy"
    except Exception as e:
        health_status["services"]["mongodb"] = f"error: {str(e)}"

    # Check Elasticsearch
    try:
        elasticsearch_healthy = await elasticsearch_service.health_check()
        health_status["services"]["elasticsearch"] = "healthy" if elasticsearch_healthy else "unhealthy"
    except Exception as e:
        health_status["services"]["elasticsearch"] = f"error: {str(e)}"

    # Check Ollama
    try:
        ollama_healthy = await ollama_service.health_check()
        health_status["services"]["ollama"] = "healthy" if ollama_healthy else "unhealthy"
    except Exception as e:
        health_status["services"]["ollama"] = f"error: {str(e)}"

    # Overall status
    all_healthy = all(
        status == "healthy"
        for status in health_status["services"].values()
    )
    health_status["status"] = "healthy" if all_healthy else "degraded"

    return health_status
