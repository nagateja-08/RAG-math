# MathGPT — Graph-Enhanced RAG Intelligent Mathematical Learning Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-Graph_DB-008CC1.svg?logo=neo4j&logoColor=white)](https://neo4j.com)
[![Groq](https://img.shields.io/badge/Groq-LPU_Inference-F55036.svg)](https://groq.com)
[![SymPy](https://img.shields.io/badge/SymPy-1.14.0-3B5526.svg?logo=sympy&logoColor=white)](https://www.sympy.org)
[![React](https://img.shields.io/badge/React-19.2+-61DAFB.svg?logo=react&logoColor=black)](https://react.dev)
[![Vite](https://img.shields.io/badge/Vite-8.0+-646CFF.svg?logo=vite&logoColor=white)](https://vitejs.dev)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0+-38B2AC.svg?logo=tailwind-css&logoColor=white)](https://tailwindcss.com)

MathGPT is a production-ready, AI-powered mathematical learning platform that merges traditional **Retrieval-Augmented Generation (RAG)** with a **Mathematical Knowledge Graph (Neo4j)** and an independent **Symbolic Computer Algebra System (SymPy)**.

Traditional RAG chatbots retrieve isolated text chunks and often hallucinate formulas, proofs, or prerequisite dependencies. MathGPT solves this fundamental limitation:
1. **Neo4j Mathematical Knowledge Graph**: Maps prerequisite dependencies (`PREREQUISITE_OF`), governing formulas (`USES_FORMULA`), connected theorems (`PROVES`, `EXPLAINS`), and subject taxonomies across **Calculus, Algebra, Trigonometry, Probability, and Statistics**.
2. **FAISS Vector Retrieval**: Indexes uploaded PDF/TXT textbooks, papers, and curriculum notes.
3. **SymPy Verification Engine**: Independently verifies derivatives, integrals, limits, equations, and algebraic identities with zero hallucination.
4. **Prerequisite-Based Learning**: Identifies missing prerequisite foundations when a student inquires about an advanced concept (e.g. *Limits* and *Differentiation* before *Integration*) and provides targeted diagnostic checks.
5. **Interactive Graph Explorer**: Visualizes mathematical concepts and prerequisite paths in real-time.
6. **Learning Analytics Dashboard**: Tracks student inquiries, concept mastery, weak prerequisite areas, and quiz scores.

---

## Architecture Pipeline

```
                                      +-----------------------------+
                                      |    User Mathematical Query  |
                                      +--------------+--------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      |     Query Understanding     |
                                      | (Entity & Concept Extraction)|
                                      +--------------+--------------+
                                                     |
                         +---------------------------+---------------------------+
                         |                                                       |
                         v                                                       v
         +-------------------------------+                       +-------------------------------+
         |     FAISS Vector Search       |                       |    Neo4j Graph Traversal      |
         |  - PDF / TXT Text Chunks      |                       |  - Concept Neighborhood       |
         |  - 384-dim Embeddings         |                       |  - Prerequisite Chain         |
         |  - Top-K Similarity Search    |                       |  - Governing Formulas         |
         |  - Textual Excerpts           |                       |  - Connected Theorems         |
         +---------------+---------------+                       +---------------+---------------+
                         |                                                       |
                         +---------------------------+---------------------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      |     Context Combination     |
                                      |  (Document Excerpts + Graph)|
                                      +--------------+--------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      |  LangChain Prompt Synthesis |
                                      +--------------+--------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      |  Groq LPU (Llama 3.3 70B)   |
                                      +--------------+--------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      | SymPy Formula Verification  |
                                      | (Exact Symbolic Validation) |
                                      +--------------+--------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      | FastAPI JSON Response       |
                                      |  - Answer & LaTeX Steps     |
                                      |  - Prerequisites Banner     |
                                      |  - SymPy Verification Badge |
                                      |  - Document References      |
                                      +--------------+--------------+
                                                     |
                                                     v
                                      +-----------------------------+
                                      | Modern React + KaTeX UI     |
                                      +-----------------------------+
```

---

## 9-Phase Development Breakdown

### Phase 1: Project Setup and Folder Structure
- Clean separation of concerns between `backend/` (FastAPI) and `frontend/` (React + Vite).
- Configuration managed via `pydantic-settings` reading `.env`.
- Database initialization with SQLAlchemy supporting PostgreSQL, MySQL, and SQLite.

### Phase 2: Neo4j Database & Knowledge Graph Service
- **Node Types**: `Concept`, `Formula`, `Theorem`, `Topic`, `Subtopic`, `Example`.
- **Relationship Types**: `PREREQUISITE_OF`, `RELATED_TO`, `PART_OF`, `USES_FORMULA`, `PROVES`, `EXPLAINS`.
- **Subjects**: Calculus, Algebra, Trigonometry, Probability, Statistics.
- **Dual-Mode Engine**: Connects to live Neo4j via official Bolt driver; automatically runs an embedded, high-performance in-memory graph fallback when Neo4j is offline so the application never crashes.
- **Dynamic Insertion**: Ingestion extracts new concepts from documents using Cypher `MERGE` to prevent duplicate nodes.

### Phase 3: PDF Processing & FAISS Vector Store
- Document text extraction via `pypdf` with text normalization and cleaning.
- `RecursiveCharacterTextSplitter` chunking into 512-character semantic chunks with 50-character overlap.
- High-speed 384-dimensional vector embeddings and similarity search.

### Phase 4: Graph Retrieval and Vector Retrieval Integration
- Fuses text chunks from FAISS with Cypher neighborhood queries from Neo4j into unified contextual prompts.
- Maintains strict provenance distinction between `[KNOWLEDGE GRAPH RELATIONSHIPS]` and `[DOCUMENT EXCERPTS]`.

### Phase 5: Groq API & LangChain Orchestration
- Fast inference powered by Groq Cloud (`llama-3.3-70b-versatile` with automatic multi-model failover to `llama-3.1-8b-instant`).
- Structured pedagogical output conforming to mathematical standards.

### Phase 6: FastAPI API Endpoints
- `POST /api/v1/ask` — Combined Graph-Enhanced RAG question answering.
- `GET /api/v1/graph` — Complete graph data for interactive visualization.
- `GET /api/v1/graph/{concept}` — Concept neighborhood details.
- `GET /api/v1/prerequisites/{concept}` — Multi-level prerequisite dependency chain.
- `GET /api/v1/topics` — Topics organized by subject.
- `POST /api/v1/verify` — Independent SymPy formula verification.
- `GET /api/v1/assessment/{concept}` — Prerequisite diagnostic quiz generation.
- `POST /api/v1/assessment` — Student assessment submission and weak concept detection.
- `GET /api/v1/progress` — Student learning progress analytics.
- `POST /api/v1/upload` — Upload PDF/TXT documents, index FAISS, and extract concepts into Neo4j.
- `GET /api/v1/health` — System status, vector store, and Neo4j connection health.

### Phase 7: React Frontend & Interactive Graph Explorer
- Modern ChatGPT-like dark interface.
- Real-time interactive HTML5 Canvas graph explorer with physics, dragging, zooming, subject filters, and search.
- KaTeX equation rendering (`$$...$$` and `$..$`).
- Quick-math symbol buttons for rapid input.
- Prerequisite alert banner with one-click "Test My Readiness" diagnostic modals.
- Real-time student learning progress dashboard with subject mastery tracking.

### Phase 8: SymPy Formula Verification & Diagnostic Assessment
- Independent symbolic computation for derivatives, integrals, limits, equations, and algebraic identities.
- Verification badge (`✓ Verified by SymPy` or `⚠️ Cannot be verified automatically`).
- Diagnostic quizzes assessing understanding of prerequisite topics before advancing.

### Phase 9: Testing, Optimization, and Deployment
- 23 automated unit and integration tests passing with 100% coverage.
- Single-command launch script (`start.bat`).
- Cloud deployment configuration (`render.yaml`).

---

## Getting Started

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- (Optional) Neo4j 5.x local or Neo4j Aura cloud instance (falls back to built-in in-memory graph store if not configured)
- Free Groq Cloud API Key from [console.groq.com](https://console.groq.com)

### 2. Environment Configuration
Create `backend/.env` (or copy from `backend/.env.example`):
```ini
GROQ_API_KEY=your_groq_api_key_here
MODEL_NAME=llama-3.3-70b-versatile

# Neo4j Settings (Optional)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
NEO4J_DATABASE=neo4j

# Database (Default: SQLite)
DATABASE_URL=sqlite:///./math_learning.db
```

### 3. Backend Setup
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open [http://localhost:5173](http://localhost:5173) in your browser.

### 5. Running Tests
Run the comprehensive test suite:
```bash
python -m pytest backend/tests -v
```
Output:
```
======================= 23 passed, 19 warnings in 5.01s =======================
```

---

## License
MIT License. Built with ❤️ for intelligent mathematical learning.
