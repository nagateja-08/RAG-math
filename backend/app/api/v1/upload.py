import os
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException

from ...core.config import get_settings
from ...models.schemas import UploadResponse
from ...services.rag.ingest import process_and_index_document

router = APIRouter()
settings = get_settings()

@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload mathematical documents (PDF or TXT):
    1. Extracts and cleans text
    2. Chunks and computes embeddings
    3. Stores embeddings in FAISS
    4. Extracts mathematical concepts and dynamically inserts them into Neo4j
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded.")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".txt", ".md"):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format '{ext}'. Only .pdf and .txt documents are allowed."
        )

    # Save to temp upload directory
    upload_dir = Path(settings.data_path)
    upload_dir.mkdir(parents=True, exist_ok=True)
    temp_path = upload_dir / file.filename

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        chunks_count, extracted_concepts = process_and_index_document(temp_path, file.filename)

        return UploadResponse(
            filename=file.filename,
            chunks_added=chunks_count,
            concepts_extracted=extracted_concepts,
            message=f"Successfully indexed {chunks_count} chunks into FAISS and synced {len(extracted_concepts)} concepts to Knowledge Graph."
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
