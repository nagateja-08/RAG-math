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
You are MathGPT — an expert AI mathematics problem solver.

STRICT DOMAIN BOUNDARY:
You answer ONLY questions about Mathematics, Calculus, Algebra, Geometry, Trigonometry, Probability, Statistics, and Quantitative Problem Solving.
If the user asks ANY non-mathematical question (e.g. politics, politicians such as "cm of telangana", current affairs, trivia, geography, movies, celebrities, weather, general chatting):
You MUST REFUSE immediately. Reply ONLY with:
"I am **MathGPT**, an AI specialized exclusively in mathematics, calculus, algebra, geometry, probability, and statistics. 

Please ask a mathematics problem or upload an image of a math question to solve!"

EXACT OUTPUT FORMAT FOR MATH PROBLEMS (Short, sweet, and direct — like an official exam answer key):

### Answer
Correct answer is **[value or simplified result]**

### Explanation
[Direct, short, and sweet mathematical derivation. No unnecessary theory or narrative filler.]
Connect equations naturally and concisely:
- State the starting identity or relationship:
  $$ [display equation] $$
- State the property, theorem, or substitution applied:
  $$ [display equation] $$
- Simplify directly:
  $$ [display equation] $$
- Conclude: Hence, the answer is [value].

STRICT PROHIBITIONS:
- ZERO extra content: NO introductory paragraphs, NO textbook theory, NO prerequisite lists, NO fake historical contexts.
- DO NOT use verbose step labels like "Step 1: Identify the role of...", "Step 2: ...".
- DO NOT include sections like "Concept Introduction", "Prerequisite Concepts", "Relevant Formulas", "Worked Example", or "Related Concepts".
- ALWAYS wrap display equations in $$...$$ on their own lines. Use $...$ for inline variables. NEVER use \\[ \\] or \\( \\).
- Keep the entire explanation short, sweet, clean, and mathematically rigorous.
"""

def check_math_relevance(query: str) -> Optional[str]:
    """
    Ensure the user query is relevant to mathematics, calculus, algebra, geometry,
    probability, statistics, or quantitative problem solving.
    Returns a strict refusal message if the query is non-mathematical.
    """
    if not query:
        return None

    q_lower = query.lower().strip()

    # Greetings & assistant identity inquiries
    if q_lower in ("hi", "hello", "hey", "good morning", "good evening", "who are you", "what can you do", "help"):
        return (
            "Hello! I am **MathGPT**, your AI mathematics solver.\n\n"
            "Ask me any problem in **Calculus, Algebra, Trigonometry, Geometry, Probability, or Statistics**, or upload an image of a math problem to solve!"
        )

    # Obvious non-math entities, politics, geography, celebrities, trivia
    non_math_patterns = [
        r'\b(?:cm|chief minister|prime minister|president|governor|mla|mp|minister|politician|politics|bjp|congress|brs|party|election|vote|parliament)\b',
        r'\b(?:capital of|currency of|population of|president of|prime minister of|ruler of|king of)\b',
        r'\b(?:who is|who was|who are|tell me about)\s+(?:the\s+)?(?:cm|pm|president|minister|actor|actress|singer|player|celebrity|ceo|founder|director|author)\b',
        r'\b(?:telangana|hyderabad|delhi|india|usa|america|russia|ukraine|china|pakistan)\b',
        r'\b(?:movie|film|cinema|actor|actress|bollywood|hollywood|tollywood|song|lyrics|cricket|football|ipl|fifa|world cup)\b',
        r'\b(?:recipe|cook|food|restaurant|dish|ingredients)\b',
        r'\b(?:weather|temperature|forecast|rain in|climate in)\b'
    ]

    # Mathematical symbols and keywords
    math_symbols = ["+", "-", "*", "/", "=", "^", "<", ">", "∫", "∑", "√", "lim", "∂", "π", "θ", "\\"]
    math_keywords = [
        "math", "solve", "calculate", "evaluate", "simplify", "derive", "integrate", "differentiate",
        "integral", "derivative", "equation", "formula", "theorem", "matrix", "vector", "polynomial",
        "quadratic", "linear", "logarithm", "exponential", "function", "limit", "series", "binomial",
        "trigonometry", "sin", "cos", "tan", "probability", "statistics", "variance", "deviation",
        "geometry", "circle", "ellipse", "parabola", "hyperbola", "triangle", "angle", "roots",
        "roots of", "value of", "find x", "find y", "equal to", "fraction", "ratio", "percentage",
        "graph", "slope", "tangent", "secant", "locus", "radius", "diameter", "modulus", "complex"
    ]

    has_math_symbols = any(sym in query for sym in math_symbols)
    has_math_keywords = any(kw in q_lower for kw in math_keywords)

    for pat in non_math_patterns:
        if re.search(pat, q_lower):
            if not has_math_symbols and not has_math_keywords:
                return (
                    "I am **MathGPT**, an AI specialized exclusively in mathematics, calculus, algebra, geometry, probability, and statistics.\n\n"
                    "I cannot answer questions unrelated to mathematics. Please ask a mathematical problem or upload an image of a math question to solve!"
                )

    return None

def normalize_math_delimiters(text: str) -> str:
    """Ensure LaTeX delimiters render properly in KaTeX without raw brackets, and ensure spacing."""
    if not text:
        return ""
    # Convert \[ ... \] to $$ ... $$ with spacing
    text = re.sub(r'\\\[(.*?)\\\]', r'\n\n$$\n\1\n$$\n\n', text, flags=re.DOTALL)
    # Convert \( ... \) to $ ... $
    text = re.sub(r'\\\((.*?)\\\)', r'$\1$', text, flags=re.DOTALL)
    # Convert standalone bracketed LaTeX expressions: [ \frac{...} ] -> $$ \frac{...} $$
    text = re.sub(
        r'(?:\n|^)\s*\[\s*([^\]\n]*?(?:\\(?:frac|text|sum|int|sqrt|lim|cdot|times|alpha|beta|theta|pi|le|ge|partial)|[\^_=])[^\]\n]*?)\s*\]\s*(?:\n|$)',
        r'\n\n$$\n\1\n$$\n\n',
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

    # Guardrail: Check for non-mathematical queries (politics, celebrities, CM/PM, general trivia)
    refusal_msg = check_math_relevance(user_q)
    if refusal_msg:
        logger.info(f"Query rejected by math relevance filter: {user_q}")
        return AskResponse(
            answer=refusal_msg,
            identified_concept=None,
            subject="Mathematics",
            prerequisites=[],
            document_references=[],
            graph_context=None,
            sympy_verification=None,
            recommended_study_topics=[],
            extracted_question=extracted_question,
            model_used=settings.model_name
        )

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
