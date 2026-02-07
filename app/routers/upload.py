"""Upload router for receipt file handling."""

import logging
from pathlib import Path
from typing import Optional

import jsonschema
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import ValidationError

from app.config import settings
from app.models import Receipt, UploadResponse
from app.services.base_llm_service import BaseLLMService
from app.services.elasticsearch_service import ElasticsearchService
from app.services.mongodb_service import MongoDBService

router = APIRouter(prefix="/api", tags=["upload"])
logger = logging.getLogger(__name__)

# Service instances (will be injected from main app)
mongodb_service: Optional[MongoDBService] = None
elasticsearch_service: Optional[ElasticsearchService] = None
llm_service: Optional[BaseLLMService] = None


def set_services(
    mongo: MongoDBService, elastic: ElasticsearchService, llm: BaseLLMService
):
    """Set service instances."""
    global mongodb_service, elasticsearch_service, llm_service
    mongodb_service = mongo
    elasticsearch_service = elastic
    llm_service = llm


@router.post("/upload", response_model=UploadResponse)
async def upload_receipt(file: UploadFile = File(...)):
    """
    Upload and analyze receipt image.

    Accepts JPG, PNG, and PDF files up to 5MB.
    Analyzes receipt using configured LLM provider, stores in MongoDB, and indexes in Elasticsearch.
    """
    try:
        # Validate file type
        file_extension = Path(file.filename).suffix.lower().replace(".", "")
        if file_extension not in settings.allowed_extensions_list:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Allowed: {', '.join(settings.allowed_extensions_list)}",
            )

        # Read file content
        content = await file.read()
        file_size = len(content)

        # Validate file size
        if file_size > settings.max_upload_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024:.1f}MB",
            )

        # Save to temporary file
        temp_file_path = (
            settings.upload_dir
            / f"{Path(file.filename).stem}_{hash(content)}.{file_extension}"
        )

        try:
            with open(temp_file_path, "wb") as f:
                f.write(content)

            # Analyze receipt with LLM service
            logger.info(f"Analyzing receipt: {file.filename}")
            receipt_data = await llm_service.analyze_receipt(temp_file_path)

            # Validate against schema
            try:
                receipt = Receipt(**receipt_data)
            except ValidationError as e:
                logger.error(f"Receipt validation failed: {e}")
                raise HTTPException(
                    status_code=422, detail=f"Receipt data validation failed: {str(e)}"
                )

            # Save to MongoDB
            receipt_id = await mongodb_service.save_receipt(receipt.model_dump())
            logger.info(f"Saved receipt to MongoDB: {receipt_id}")

            # Index in Elasticsearch
            await elasticsearch_service.index_receipt(receipt_id, receipt.model_dump())
            logger.info(f"Indexed receipt in Elasticsearch: {receipt_id}")

            return UploadResponse(
                success=True,
                receipt_id=receipt_id,
                receipt=receipt,
                message="Receipt analyzed and saved successfully",
            )

        finally:
            # Clean up temporary file
            if temp_file_path.exists():
                temp_file_path.unlink()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {e}", exc_info=True)
        return UploadResponse(
            success=False, message="Failed to process receipt", error=str(e)
        )
