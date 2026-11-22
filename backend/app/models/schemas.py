from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# ----------------- Chat & Ask Schemas -----------------

class ChatMessage(BaseModel):
    role: str
    content: str

class AskRequest(BaseModel):
    question: Optional[str] = ""
    history: Optional[List[ChatMessage]] = []
    user_id: Optional[str] = "default_student"
    use_vector_search: Optional[bool] = True
    use_graph_retrieval: Optional[bool] = True
    use_sympy_verification: Optional[bool] = True
    image_data: Optional[str] = None  # Base64 image (data:image/... or raw base64)

class SymPyVerificationResult(BaseModel):
    is_verified: bool
    status: str  # verified, refuted, unverified, not_applicable
    expression: Optional[str] = None
    operation: Optional[str] = None
    symbolic_result: Optional[str] = None
    latex_output: Optional[str] = None
    error_message: Optional[str] = None

class ConceptPrerequisiteInfo(BaseModel):
    name: str
    difficulty: Optional[str] = "Intermediate"
    subject: Optional[str] = None
    is_weak: Optional[bool] = False

class GraphContextItem(BaseModel):
    concept: str
    subject: Optional[str] = None
    difficulty: Optional[str] = None
    description: Optional[str] = None
    prerequisites: List[str] = []
    formulas: List[Dict[str, str]] = []
    theorems: List[Dict[str, str]] = []
    related_concepts: List[str] = []

class AskResponse(BaseModel):
    answer: str
    identified_concept: Optional[str] = None
    subject: Optional[str] = None
    prerequisites: List[ConceptPrerequisiteInfo] = []
    document_references: List[str] = []
    graph_context: Optional[GraphContextItem] = None
    sympy_verification: Optional[SymPyVerificationResult] = None
    recommended_study_topics: List[str] = []
    extracted_question: Optional[str] = None
    model_used: str

class ChatRequest(BaseModel):
    message: str
    history: Optional[List[ChatMessage]] = []
    stream: Optional[bool] = False

class ChatResponse(BaseModel):
    answer: str
    context_used: Optional[List[str]] = []
    sympy_result: Optional[Dict[str, Any]] = None
    model: str

# ----------------- Knowledge Graph Schemas -----------------

class GraphNode(BaseModel):
    id: str
    name: str
    type: str  # Concept, Formula, Theorem, Topic, Subtopic, Example
    subject: Optional[str] = None
    difficulty: Optional[str] = "Intermediate"
    description: Optional[str] = None
    latex: Optional[str] = None
    source: Optional[str] = "Curriculum"

class GraphEdge(BaseModel):
    source: str
    target: str
    type: str  # PREREQUISITE_OF, RELATED_TO, PART_OF, USES_FORMULA, PROVES, EXPLAINS
    description: Optional[str] = None

class GraphDataResponse(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    total_nodes: int
    total_edges: int

class ConceptDetailResponse(BaseModel):
    concept: str
    node: GraphNode
    prerequisites: List[GraphNode] = []
    dependents: List[GraphNode] = []
    formulas: List[GraphNode] = []
    theorems: List[GraphNode] = []
    related: List[GraphNode] = []

class PrerequisitePathNode(BaseModel):
    name: str
    difficulty: str
    subject: str
    depth: int

class PrerequisiteTreeResponse(BaseModel):
    target_concept: str
    direct_prerequisites: List[str]
    prerequisite_chain: List[PrerequisitePathNode]
    readiness_assessment_available: bool

class TopicsResponse(BaseModel):
    subjects: List[str]
    topics_by_subject: Dict[str, List[str]]
    total_concepts: int

# ----------------- SymPy Formula Verification Schemas -----------------

class VerifyRequest(BaseModel):
    expression: str
    operation: str = "solve"  # solve, differentiate, integrate, simplify, equality_check, limit
    variable: Optional[str] = "x"
    target_equals: Optional[str] = None  # for equality_check
    lower_bound: Optional[str] = None
    upper_bound: Optional[str] = None
    limit_point: Optional[str] = "0"

class VerifyResponse(BaseModel):
    success: bool
    verified: bool
    operation: str
    input_expression: str
    symbolic_result: Optional[str] = None
    latex_output: Optional[str] = None
    comparison_target: Optional[str] = None
    is_equal: Optional[bool] = None
    message: str

# ----------------- Assessment & Learning Analytics Schemas -----------------

class QuizOption(BaseModel):
    id: str
    text: str

class AssessmentQuestion(BaseModel):
    id: int
    concept: str
    question: str
    latex_formula: Optional[str] = None
    options: List[QuizOption]
    explanation: str

class AssessmentQuizResponse(BaseModel):
    target_concept: str
    prerequisite_concepts: List[str]
    questions: List[AssessmentQuestion]

class UserAnswer(BaseModel):
    question_id: int
    selected_option: str

class AssessmentSubmitRequest(BaseModel):
    user_id: Optional[str] = "default_student"
    target_concept: str
    answers: List[UserAnswer]

class AssessmentSubmitResponse(BaseModel):
    score_percentage: float
    total_questions: int
    correct_count: int
    passed: bool
    weak_prerequisites: List[str]
    recommended_topics: List[str]
    detailed_feedback: List[Dict[str, Any]]

class TopicProgressItem(BaseModel):
    concept: str
    subject: str
    status: str
    mastery_score: float

class ProgressSummaryResponse(BaseModel):
    user_id: str
    total_questions_asked: int
    concepts_mastered: int
    weak_concepts: List[str]
    average_assessment_score: float
    recent_activity: List[Dict[str, Any]]
    recommended_study_plan: List[str]
    mastery_by_subject: Dict[str, float]

# ----------------- Document & System Schemas -----------------

class UploadResponse(BaseModel):
    filename: str
    chunks_added: int
    concepts_extracted: List[str]
    message: str

class HealthResponse(BaseModel):
    status: str
    llm_connected: bool
    vector_store_loaded: bool
    neo4j_connected: bool
    neo4j_mode: str  # live_neo4j or in_memory_resilient_store
    total_graph_nodes: int
    model_name: str
