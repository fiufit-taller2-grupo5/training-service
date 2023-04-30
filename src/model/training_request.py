from pydantic import BaseModel


class TrainingRequest(BaseModel):
    title: str = "Default title"
    description: str = None
    multimedia: str = None
    state: str = "active"
    difficulty: int = None
    type: str = "default"
    trainer_id: int = None
    multimedia_id: int = None
