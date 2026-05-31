"""
Data Ingestion Script for MathGPT RAG Pipeline
Reads all CSV datasets, chunks them, embeds them, and saves FAISS index.
"""

import os
import sys
import pandas as pd
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings

# Add parent to path
sys.path.append(str(Path(__file__).resolve().parents[3]))
from app.core.config import get_settings

settings = get_settings()

# ────────────────────────────────────────────
# CSV Schema Definitions
# ────────────────────────────────────────────
CSV_SCHEMAS = {
    "MetaMathQA.csv": {
        "question_col": "query",
        "answer_col": "response",
        "max_rows": 100,
        "description": "MetaMathQA - augmented math QA dataset"
    },
    "algebra.csv": {
        "question_col": "problem",
        "answer_col": "solution",
        "max_rows": 200,
        "description": "MATH Algebra dataset"
    },
    "hendrycks_math_complete.csv": {
        "question_col": "problem",
        "answer_col": "solution",
        "max_rows": 200,
        "description": "Hendrycks Complete MATH dataset"
    },
    "test-00000-of-00001.csv": {
        "question_col": "question",
        "answer_col": "answer",
        "max_rows": 100,
        "description": "GSM8K Test set"
    },
    "train-00000-of-00001.csv": {
        "question_col": "question",
        "answer_col": "answer",
        "max_rows": 200,
        "description": "GSM8K Train set"
    }
}



def load_and_format_csvs(data_path: str) -> list:
    """Load all CSVs and return a list of formatted text documents."""
    documents = []
    data_dir = Path(data_path)

    for filename, schema in CSV_SCHEMAS.items():
        filepath = data_dir / filename
        if not filepath.exists():
            print(f"[SKIP] {filename} - not found.")
            continue

        print(f"[LOAD] {schema['description']} ({filename})...")
        try:
            df = pd.read_csv(
                filepath,
                nrows=schema["max_rows"],
                on_bad_lines="skip",
                engine="python"
            )

            q_col = schema["question_col"]
            a_col = schema["answer_col"]

            if q_col not in df.columns or a_col not in df.columns:
                print(f"  [ERROR] Missing columns in {filename}. Found: {list(df.columns)}")
                continue

            # Drop nulls
            df = df[[q_col, a_col]].dropna()

            count = 0
            for _, row in df.iterrows():
                question = str(row[q_col]).strip()
                answer = str(row[a_col]).strip()

                if len(question) < 5 or len(answer) < 5:
                    continue

                # Format as Q&A text chunk
                text = f"Question: {question}\n\nSolution: {answer}"
                documents.append(text)
                count += 1

            print(f"  [OK] Loaded {count} Q&A pairs from {filename}")

        except Exception as e:
            print(f"  [ERROR] Error loading {filename}: {e}")

    print(f"\n[INFO] Total documents loaded: {len(documents)}")
    return documents


def chunk_documents(documents: list, chunk_size: int, chunk_overlap: int) -> list:
    """Split documents into chunks for embedding."""
    print(f"\n[CHUNK] Chunking {len(documents)} documents...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\nSolution:", "\n\n", "\n", ". ", " "]
    )

    chunks = []
    for doc in documents:
        splits = splitter.split_text(doc)
        chunks.extend(splits)

    print(f"  [OK] Created {len(chunks)} chunks")
    return chunks


def build_faiss_index(chunks: list, embedding_model: str, save_path: str):
    """Create FAISS index from chunks and save to disk."""
    print(f"\n[EMBED] Building FAISS index with model: {embedding_model}")
    print("  (This may take several minutes...)")

    embeddings = HuggingFaceInferenceAPIEmbeddings(
        api_key=settings.hf_api_key,
        model_name=f"sentence-transformers/{embedding_model}",
    )

    # Build FAISS from texts in batches
    batch_size = 1000
    vectorstore = None

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        batch_num = i // batch_size + 1
        total_batches = (len(chunks) // batch_size) + 1
        print(f"  [BATCH] Processing batch {batch_num}/{total_batches} ({len(batch)} chunks)...")

        if vectorstore is None:
            vectorstore = FAISS.from_texts(batch, embeddings)
        else:
            batch_store = FAISS.from_texts(batch, embeddings)
            vectorstore.merge_from(batch_store)

    # Save index
    os.makedirs(save_path, exist_ok=True)
    vectorstore.save_local(save_path)
    print(f"\n[DONE] FAISS index saved to: {save_path}")
    return vectorstore


def main():
    print("=" * 60)
    print("MathGPT RAG Ingestion Pipeline")
    print("=" * 60)

    # Step 1: Load CSVs
    documents = load_and_format_csvs(settings.data_path)
    if not documents:
        print("[ERROR] No documents loaded. Exiting.")
        return

    # Step 2: Chunk
    chunks = chunk_documents(documents, settings.chunk_size, settings.chunk_overlap)

    # Step 3: Build & Save FAISS Index
    build_faiss_index(chunks, settings.embedding_model, settings.vector_store_path)

    print("\n[SUCCESS] Ingestion complete! MathGPT is ready for semantic search.")


if __name__ == "__main__":
    main()
