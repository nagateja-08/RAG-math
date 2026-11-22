from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.schemas import AssessmentQuizResponse, AssessmentSubmitRequest, AssessmentSubmitResponse
from ...services.learning.assessment_service import get_assessment_for_concept, evaluate_assessment
from ...services.learning.progress_service import record_assessment

router = APIRouter()

@router.get("/assessment/{concept}", response_model=AssessmentQuizResponse)
def get_quiz(concept: str):
    """
    Generate diagnostic questions for an advanced concept and its prerequisites (Feature 2).
    """
    try:
        quiz = get_assessment_for_concept(concept)
        return quiz
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate assessment: {str(e)}")

@router.post("/assessment", response_model=AssessmentSubmitResponse)
def submit_quiz(request: AssessmentSubmitRequest, db: Session = Depends(get_db)):
    """
    Submit student answers, score them, update learning progress,
    and detect weak prerequisite topics.
    """
    answers_dicts = [{"question_id": a.question_id, "selected_option": a.selected_option} for a in request.answers]
    eval_res = evaluate_assessment(request.target_concept, answers_dicts)

    # Persist in learning progress database
    record_assessment(
        db=db,
        user_id=request.user_id or "default_student",
        target_concept=request.target_concept,
        eval_res=eval_res
    )

    return AssessmentSubmitResponse(
        score_percentage=eval_res["score_percentage"],
        total_questions=eval_res["total_questions"],
        correct_count=eval_res["correct_count"],
        passed=eval_res["passed"],
        weak_prerequisites=eval_res["weak_prerequisites"],
        recommended_topics=eval_res["recommended_topics"],
        detailed_feedback=eval_res["detailed_feedback"]
    )
