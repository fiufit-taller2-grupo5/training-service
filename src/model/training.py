from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Training(Base):
    __tablename__ = "TrainingPlan"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    description = Column(String)
    multimedia = Column(String)
    state = Column(String)
    difficulty = Column(Integer)
    type = Column(String)
    trainer_id = Column(Integer)
    multimedia_id = Column(Integer)

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
