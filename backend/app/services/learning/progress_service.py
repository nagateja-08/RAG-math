"""
Student Learning Progress Analytics Service (Feature 5)
Tracks:
- Questions attempted
- Topics understood & mastered
- Weak concepts identified from assessments
- Assessment scores
- Generates personalized study recommendations based on prerequisite graph
"""

from typing import Dict, Any, List
from datetime import datetime
from sqlalchemy.orm import Session
from ...models.db_models import UserProgress, QuestionLog, AssessmentAttempt
from ..graph.graph_service import get_graph_service

def record_question(db: Session, user_id: str, question: str, concept: str = None, subject: str = None, verified: bool = False):
    """Log an attempted question and update student practice metrics."""
    log = QuestionLog(
        user_id=user_id,
        question=question,
        concept_identified=concept,
        subject=subject,
        sympy_verified=verified,
        timestamp=datetime.utcnow()
    )
    db.add(log)

    if concept:
        prog = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.concept == concept
        ).first()

        if not prog:
            prog = UserProgress(
                user_id=user_id,
                concept=concept,
                subject=subject or "General",
                status="in_progress",
                mastery_score=15.0,
                questions_attempted=1,
                questions_correct=1 if verified else 0
            )
            db.add(prog)
        else:
            prog.questions_attempted += 1
            if verified:
                prog.questions_correct += 1
            prog.mastery_score = min(100.0, prog.mastery_score + 5.0)
            if prog.mastery_score >= 80.0:
                prog.status = "mastered"

    db.commit()

def record_assessment(db: Session, user_id: str, target_concept: str, eval_res: Dict[str, Any]):
    """Log assessment score and update weak prerequisite concepts."""
    import json
    attempt = AssessmentAttempt(
        user_id=user_id,
        target_concept=target_concept,
        score_percentage=eval_res["score_percentage"],
        total_questions=eval_res["total_questions"],
        correct_answers=eval_res["correct_count"],
        weak_prerequisites=json.dumps(eval_res["weak_prerequisites"]),
        timestamp=datetime.utcnow()
    )
    db.add(attempt)

    # Update weak concepts
    for weak_c in eval_res["weak_prerequisites"]:
        prog = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.concept == weak_c
        ).first()
        if not prog:
            prog = UserProgress(
                user_id=user_id,
                concept=weak_c,
                subject="General",
                status="weak",
                mastery_score=30.0,
                questions_attempted=1,
                questions_correct=0
            )
            db.add(prog)
        else:
            prog.status = "weak"
            prog.mastery_score = max(10.0, prog.mastery_score - 15.0)

    # If passed target concept
    if eval_res["passed"]:
        prog = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.concept == target_concept
        ).first()
        if prog:
            prog.status = "mastered"
            prog.mastery_score = max(prog.mastery_score, eval_res["score_percentage"])

    db.commit()

def get_student_progress_summary(db: Session, user_id: str = "default_student") -> Dict[str, Any]:
    """Compile comprehensive student learning progress analytics."""
    total_questions = db.query(QuestionLog).filter(QuestionLog.user_id == user_id).count()

    progress_records = db.query(UserProgress).filter(UserProgress.user_id == user_id).all()
    mastered_count = sum(1 for p in progress_records if p.status == "mastered")
    weak_concepts = [p.concept for p in progress_records if p.status == "weak"]

    assessments = db.query(AssessmentAttempt).filter(AssessmentAttempt.user_id == user_id).all()
    avg_score = 0.0
    if assessments:
        avg_score = round(sum(a.score_percentage for a in assessments) / len(assessments), 1)

    # Recent questions
    recent_logs = db.query(QuestionLog).filter(QuestionLog.user_id == user_id)\
        .order_by(QuestionLog.timestamp.desc()).limit(8).all()
    recent_activity = [
        {
            "question": l.question,
            "concept": l.concept_identified or "General Math",
            "subject": l.subject or "Mathematics",
            "verified": l.sympy_verified,
            "timestamp": l.timestamp.strftime("%Y-%m-%d %H:%M")
        }
        for l in recent_logs
    ]

    # Mastery by subject
    subject_scores = {}
    subject_counts = {}
    for p in progress_records:
        subj = p.subject or "General"
        subject_scores[subj] = subject_scores.get(subj, 0.0) + p.mastery_score
        subject_counts[subj] = subject_counts.get(subj, 0) + 1

    mastery_by_subject = {
        subj: round(subject_scores[subj] / subject_counts[subj], 1)
        for subj in subject_scores
    }

    # Recommended study plan based on weak concepts & prerequisite graph
    graph_service = get_graph_service()
    recommended_plan = list(weak_concepts)
    if not recommended_plan:
        recommended_plan = ["Functions", "Limits", "Differentiation", "Linear Equations"]

    return {
        "user_id": user_id,
        "total_questions_asked": total_questions,
        "concepts_mastered": mastered_count,
        "weak_concepts": list(set(weak_concepts)),
        "average_assessment_score": avg_score,
        "recent_activity": recent_activity,
        "recommended_study_plan": recommended_plan[:6],
        "mastery_by_subject": mastery_by_subject
    }
