from pydantic import BaseModel
from datetime import datetime


class TrainingPlanRequest(BaseModel):
    title: str = "Default title"
    description: str = None
    state: str = "active"
    difficulty: int = None
    type: str = None
    trainerId: int = None
    location: str = None
    start: str = None
    end: str = None
    days: str = None


class PlanReviewRequest(BaseModel):
    comment: str = None
    score: int = None


class UserTrainingRequest(BaseModel):
    distance: float = None
    duration: str = None
    steps: int = None
    calories: int = None
    date: datetime = None


class IntervalUserTrainingRequest(BaseModel):
    start: datetime = None
    end: datetime = None


class IntervalTrainingPlanRequest(BaseModel):
    start: str = None
    end: str = None
    days: str = None
