"""
Combined Graph-Enhanced RAG Orchestrator for MathGPT (Section 4)
Orchestrates:
User Question
→ Query Understanding
→ FAISS Similarity Search
→ Neo4j Graph Retrieval
→ Context Combination
→ LangChain Prompt Construction
→ Groq LLM
→ Mathematical Answer
→ SymPy Verification Check
→ FastAPI Response
"""

import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from ...core.config import get_settings
from ..rag.retriever import retrieve_context, format_context_for_prompt
from ..graph.graph_service import get_graph_service
from ..math_engine.sympy_service import auto_extract_and_verify, verify_expression
from .groq_client import chat_completion, extract_math_from_image
from ...models.schemas import (
    AskRequest, AskResponse, GraphContextItem,
    ConceptPrerequisiteInfo, SymPyVerificationResult
)

logger = logging.getLogger("mathgpt.orchestrator")
settings = get_settings()

MATH_SYSTEM_PROMPT = """
You are MathGPT — an expert, ultra-concise AI mathematics solver.

PRIMARY DIRECTIVE:
Provide clear, optimal, step-by-step mathematical solutions without unnecessary filler, excessive background theory, or unwanted structured templates.

STRICT FORMATTING & DELIMITER RULES:
1. For display equations on their own line, ALWAYS use double dollar signs: $$ ... $$
2. For inline math variables, expressions, or numbers, ALWAYS use single dollar signs: $ ... $
3. NEVER use square brackets `\\[ ... \\]` or `\\( ... \\)` for math.
4. NEVER output raw unrendered braces `{` `}` or brackets `[` `]` in plain text. Every formula must be wrapped inside `$$` or `$`.
5. Keep explanations direct, clean, and easy to read.

OUTPUT FORMAT FOR MATH PROBLEMS:
### Solution
- Step 1: [Short explanation of step]
  $$ [Equation] $$
- Step 2: [Short explanation of step]
  $$ [Equation] $$
(Continue concisely until the problem is solved)

### Final Answer
$$ \\boxed{\\text{Result}} $$
[One short, clear summary sentence stating the final answer]

BANNED CONTENT — DO NOT INCLUDE ANY OF THE FOLLOWING:
- DO NOT generate "1. Concept Introduction" or long background theory.
- DO NOT generate "2. Prerequisite Concepts" or bullet lists of foundational definitions.
- DO NOT generate "3. Relevant Formulas & Theorems" lists before solving.
- DO NOT generate "5. Worked Example" or numerical table checks (the Solution IS the worked example).
- DO NOT generate "6. Mathematical Verification" tables or redundant alternate proofs.
- DO NOT generate "7. Related Concepts for Further Learning" tables or recommendations.
- Keep explanations tight, mathematically sound, clean, and directly answering what was asked.
"""

def normalize_math_delimiters(text: str) -> str:
    """Ensure LaTeX delimiters render properly in KaTeX without raw brackets or exposed symbols."""
    if not text:
        return ""
    # Convert \[ ... \] to $$ ... $$
    text = re.sub(r'\\\[(.*?)\\\]', r'$$\1$$', text, flags=re.DOTALL)
    # Convert \( ... \) to $ ... $
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    # Convert standalone bracketed LaTeX expressions: [ \frac{...} ] -> $$ \frac{...} $$
    text = re.sub(
        r'(?:\n|^)\s*\[\s*([^\]\n]*?(?:\\(?:frac|text|sum|int|sqrt|lim|cdot|times|alpha|beta|theta|pi|le|ge|partial)|[\^_=])[^\]\n]*?)\s*\]\s*(?:\n|$)',
        r'\n$$\n\1\n$$\n',
        text
    )
    return text

def extract_primary_concept(query: str) -> Optional[str]:
    """Identify the primary mathematical concept from the user question."""
    graph_service = get_graph_service()

    # 1. Check exact/fuzzy match against knowledge graph nodes
    direct_match = graph_service.find_concept(query)
    if direct_match:
        return direct_match["name"]

    # 2. Keyword heuristic scanning
    candidates = [
        "Integration by Parts", "Integration", "Differentiation", "Derivative Rules",
        "Limits", "Continuity", "Differential Equations", "Taylor Series",
        "Quadratic Equations", "Linear Equations", "Polynomials", "Matrices",
        "Determinants", "Eigenvalues and Eigenvectors",
        "Unit Circle", "Trigonometric Functions", "Trigonometric Identities", "Inverse Trigonometric Functions",
        "Sample Space and Events", "Conditional Probability", "Bayes Theorem", "Expected Value",
        "Measures of Central Tendency", "Variance and Standard Deviation", "Z-Score", "Hypothesis Testing", "Linear Regression"
    ]
    query_lower = query.lower()
    for c in candidates:
        if c.lower() in query_lower:
            return c

    # 3. Fallback search query words
    words = [w for w in re.findall(r'\b[a-zA-Z]{4,}\b', query) if w.lower() not in ("what", "how", "solve", "explain", "calculate", "find", "about")]
    for w in words:
        found = graph_service.search_concepts(w, limit=1)
        if found:
            return found[0]["name"]

    return None

def execute_combined_pipeline(request: AskRequest, db: Optional[Session] = None) -> AskResponse:
    """
    Executes the complete Graph-Enhanced RAG pipeline.
    Supports text questions and mathematical question extraction from image uploads.
    """
    user_q = (request.question or "").strip()
    extracted_question = None

    # Step 0: Image Vision Extraction (Feature 1: Multimodal Math Problem Solving)
    if request.image_data:
        logger.info("Image data detected in request. Performing mathematical vision transcription...")
        extracted_question = extract_math_from_image(request.image_data)
        if extracted_question:
            logger.info(f"Extracted question from image: {extracted_question}")
            generic_phrases = {
                "", "solve", "solve this", "solve this problem", "what is this",
                "calculate", "evaluate", "help me solve this", "solve the problem in this image",
                "solve the problem in the image"
            }
            if user_q.lower().strip() in generic_phrases:
                user_q = extracted_question
            else:
                user_q = f"Question from uploaded image:\n{extracted_question}\n\nAdditional user instructions: {user_q}"
        else:
            if not user_q:
                user_q = "Please solve the mathematical problem provided in the uploaded image."

    logger.info(f"Processing question: {user_q}")

    # 1. Query Understanding & Concept Identification
    primary_concept = extract_primary_concept(user_q)
    logger.info(f"Identified primary concept: {primary_concept}")

    # 2. FAISS Similarity Search
    doc_chunks = []
    if request.use_vector_search:
        doc_chunks = retrieve_context(user_q, top_k=settings.top_k_results)

    formatted_docs = format_context_for_prompt(doc_chunks)

    # 3. Neo4j Graph Retrieval
    graph_context_item = None
    prereq_list: List[ConceptPrerequisiteInfo] = []
    recommended_topics: List[str] = []
    subject = "Mathematics"

    if request.use_graph_retrieval and primary_concept:
        graph_service = get_graph_service()
        neighborhood = graph_service.get_concept_neighborhood(primary_concept)
        subject = neighborhood.get("subject", "Mathematics")

        graph_context_item = GraphContextItem(
            concept=neighborhood["concept"],
            subject=neighborhood["subject"],
            difficulty=neighborhood["difficulty"],
            description=neighborhood["description"],
            prerequisites=neighborhood["prerequisites"],
            formulas=neighborhood["formulas"],
            theorems=neighborhood["theorems"],
            related_concepts=neighborhood["related_concepts"]
        )

        for p in neighborhood["prerequisites"]:
            prereq_list.append(ConceptPrerequisiteInfo(
                name=p,
                difficulty="Intermediate",
                subject=subject,
                is_weak=False
            ))

        recommended_topics = neighborhood["dependents"] + neighborhood["related_concepts"]

    # 4. Context Combination
    graph_prompt_text = "No explicit graph relationships mapped for this specific query."
    if graph_context_item:
        formulas_str = ", ".join([f"{f['name']} ($${f['latex']}$$)" for f in graph_context_item.formulas]) if graph_context_item.formulas else "None"
        theorems_str = ", ".join([f"{t['name']}" for t in graph_context_item.theorems]) if graph_context_item.theorems else "None"
        prereqs_str = ", ".join(graph_context_item.prerequisites) if graph_context_item.prerequisites else "None"
        related_str = ", ".join(graph_context_item.related_concepts) if graph_context_item.related_concepts else "None"

        graph_prompt_text = (
            f"Concept: {graph_context_item.concept} (Subject: {graph_context_item.subject}, Level: {graph_context_item.difficulty})\n"
            f"Description: {graph_context_item.description}\n"
            f"Direct Prerequisites: {prereqs_str}\n"
            f"Governing Formulas: {formulas_str}\n"
            f"Associated Theorems: {theorems_str}\n"
            f"Related Topics: {related_str}"
        )

    combined_context = (
        f"=== KNOWLEDGE GRAPH RELATIONSHIPS (Neo4j) ===\n{graph_prompt_text}\n\n"
        f"=== DOCUMENT EXCERPTS (FAISS Vector Store) ===\n{formatted_docs}"
    )

    # 5. LangChain / Groq Prompt Construction
    messages = [
        {"role": "system", "content": MATH_SYSTEM_PROMPT},
        {"role": "system", "content": f"Context for this question:\n{combined_context}"}
    ]

    if request.history:
        for msg in request.history[-6:]:
            messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": user_q})

    # 6. Groq LLM Synthesis
    llm_answer = chat_completion(messages)
    llm_answer = normalize_math_delimiters(llm_answer)

    # 7. SymPy Mathematical Verification Check (Feature 4)
    sympy_result = None
    if request.use_sympy_verification:
        auto_ver = auto_extract_and_verify(user_q) or auto_extract_and_verify(llm_answer)
        if auto_ver:
            sympy_result = SymPyVerificationResult(
                is_verified=auto_ver.get("verified", False),
                status="verified" if auto_ver.get("verified") else "unverified",
                expression=auto_ver.get("input_expression"),
                operation=auto_ver.get("operation"),
                symbolic_result=auto_ver.get("symbolic_result"),
                latex_output=auto_ver.get("latex_output"),
                error_message=auto_ver.get("error_message")
            )
        else:
            sympy_result = SymPyVerificationResult(
                is_verified=False,
                status="not_applicable",
                error_message="No closed-form calculation pattern detected for automated SymPy verification."
            )

    # 8. Learning Progress Logging (Feature 5)
    if db:
        from ..learning.progress_service import record_question
        record_question(
            db=db,
            user_id=request.user_id or "default_student",
            question=user_q,
            concept=primary_concept,
            subject=subject,
            verified=(sympy_result.is_verified if sympy_result else False)
        )

    doc_sources = [d.metadata.get("source", "Document") for d in doc_chunks]

    return AskResponse(
        answer=llm_answer,
        identified_concept=primary_concept,
        subject=subject,
        prerequisites=prereq_list,
        document_references=list(set(doc_sources)),
        graph_context=graph_context_item,
        sympy_verification=sympy_result,
        recommended_study_topics=recommended_topics[:4],
        extracted_question=extracted_question,
        model_used=settings.model_name
    )
