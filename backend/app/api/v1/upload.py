"""
Upload Router - handles PDF and CSV uploads for RAG ingestion
"""

import os
import shutil
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFLoader

from ...core.config import get_settings
from ...services.rag.retriever import get_vectorstore, get_embeddings
from ...models.schemas import UploadResponse

router = APIRouter()
settings = get_settings()


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload a PDF or text file and add it to the RAG knowledge base."""
    allowed_types = [".pdf", ".txt"]
    ext = os.path.splitext(file.filename)[1].lower()

    if ext not in allowed_types:
        raise HTTPException(status_code=400, detail=f"Only {allowed_types} files are allowed.")

    # Save temp file
    temp_path = os.path.join(tempfile.gettempdir(), file.filename)
    try:
        with open(temp_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        # Load document
        if ext == ".pdf":
            loader = PyPDFLoader(temp_path)
            docs = loader.load()
            texts = [doc.page_content for doc in docs]
        else:
            with open(temp_path, "r", encoding="utf-8") as f:
                texts = [f.read()]

        # Chunk
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )
        chunks = []
        for text in texts:
            chunks.extend(splitter.split_text(text))

        # Add to vectorstore
        vs = get_vectorstore()
        embeddings = get_embeddings()
        new_store = FAISS.from_texts(chunks, embeddings)
        vs.merge_from(new_store)
        vs.save_local(settings.vector_store_path)

        return UploadResponse(
            filename=file.filename,
            message=f"Successfully added {len(chunks)} chunks to the knowledge base.",
            chunks_added=len(chunks)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
