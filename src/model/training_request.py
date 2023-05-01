from pydantic import BaseModel


class TrainingRequest(BaseModel):
    title: str = "Default title"
    description: str = None
    state: str = "active"
    difficulty: int = None
    type: str = None
    trainerId: int = None
