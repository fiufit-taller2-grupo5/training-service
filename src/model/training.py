from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Training(Base):
    __tablename__ = "TrainingPlan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, default="Default title")
    description = Column(String, nullable=True)
    multimedia = Column(String, nullable=True)
    state = Column(String, default="active")
    difficulty = Column(Integer, nullable=True)
    type = Column(String, default="defult")
    trainer_id = Column(Integer, nullable=True)
    multimedia_id = Column(Integer, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "multimedia": self.multimedia,
            "state": self.state,
            "difficulty": self.difficulty,
            "type": self.type,
            "trainer_id": self.trainer_id,
            "multimedia_id": self.multimedia_id
        }
