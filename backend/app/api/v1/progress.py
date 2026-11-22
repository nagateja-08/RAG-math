from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from ...core.database import get_db
from ...models.schemas import ProgressSummaryResponse
from ...services.learning.progress_service import get_student_progress_summary

router = APIRouter()

@router.get("/progress", response_model=ProgressSummaryResponse)
def get_progress(user_id: str = Query("default_student"), db: Session = Depends(get_db)):
    """
    Retrieve comprehensive student learning progress analytics (Feature 5):
    - Questions attempted
    - Topics understood & mastered
    - Weak concepts
    - Assessment score trends
    - Recommended study plan based on knowledge graph
    """
    return get_student_progress_summary(db=db, user_id=user_id)
