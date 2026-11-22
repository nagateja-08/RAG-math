from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey
from ..core.database import Base

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True, default="default_student")
    concept = Column(String(128), index=True)
    subject = Column(String(64), index=True)
    status = Column(String(32), default="in_progress")  # in_progress, mastered, weak
    mastery_score = Column(Float, default=0.0)          # 0.0 to 100.0
    questions_attempted = Column(Integer, default=0)
    questions_correct = Column(Integer, default=0)
    last_practiced = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class QuestionLog(Base):
    __tablename__ = "question_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True, default="default_student")
    question = Column(Text, nullable=False)
    concept_identified = Column(String(128), nullable=True)
    subject = Column(String(64), nullable=True)
    sympy_verified = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class AssessmentAttempt(Base):
    __tablename__ = "assessment_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(64), index=True, default="default_student")
    target_concept = Column(String(128), nullable=False)
    score_percentage = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    weak_prerequisites = Column(Text, default="[]")  # JSON string of weak prerequisite concepts
    timestamp = Column(DateTime, default=datetime.utcnow)
