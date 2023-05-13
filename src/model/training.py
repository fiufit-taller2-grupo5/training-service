from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class Training(Base):
    __tablename__ = "TrainingPlan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, default="Default title")
    description = Column(String, nullable=True)
    state = Column(String, default="active")
    difficulty = Column(Integer, nullable=True)
    type = Column(String, default="default")
    trainerId = Column(Integer, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "state": self.state,
            "difficulty": self.difficulty,
            "type": self.type,
            "trainerId": self.trainerId,
            "description": self.description,
        }


class UserFavoriteTrainingPlan(Base):
    __tablename__ = "UserFavoriteTrainingPlan"

    userId = Column(Integer, primary_key=True)
    trainingPlanId = Column(Integer, primary_key=True)

    def as_dict(self):
        return {
            "userId": self.userId,
            "trainingPlanId": self.trainingPlanId,
        }


class PlanReview(Base):
    __tablename__ = "PlanReview"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=True)
    comment = Column(String, nullable=True)
    score = Column(Integer, nullable=True)
    trainingPlanId = Column(Integer, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "comment": self.comment,
            "score": self.score,
            "trainingPlanId": self.trainingPlanId,
        }
