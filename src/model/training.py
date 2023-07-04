import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class TrainingPlan(Base):
    __tablename__ = "TrainingPlan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, default="Default title")
    description = Column(String, nullable=True)
    state = Column(String, default="active")
    difficulty = Column(Integer, nullable=True)
    type = Column(String, default="default")
    trainerId = Column(Integer, nullable=True)
    location = Column(String, nullable=True)
    latitude = Column(String, nullable=True)
    longitude = Column(String, nullable=True)
    start = Column(Integer, nullable=True)
    end = Column(Integer, nullable=True)
    days = Column(String, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "state": self.state,
            "difficulty": self.difficulty,
            "type": self.type,
            "trainerId": self.trainerId,
            "description": self.description,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "start": self.start,
            "end": self.end,
            "days": self.days,
        }
    
class AthleteGoal(Base):
    __tablename__ = "AthleteGoal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=True)
    description = Column(String, nullable=True)
    type = Column(String, nullable=True)
    metric = Column(Integer, nullable=True)
    athleteId = Column(Integer, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "type": self.type,
            "metric": self.metric,
            "athleteId": self.athleteId,
        }



class Multimedia(Base):
    __tablename__ = "Multimedia"

    id = Column(Integer, primary_key=True, autoincrement=True)
    fileUrl = Column(String, nullable=True)
    type = Column(String, nullable=True)
    trainingPlanId = Column(Integer, nullable=True)

    def as_dict(self):
        return {
            "id": self.id,
            "fileUrl": self.fileUrl,
            "type": self.type,
            "trainingPlanId": self.trainingPlanId,
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


class UserTraining(Base):
    __tablename__ = "UserTraining"

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(Integer, nullable=True)
    distance = Column(Integer, nullable=True)
    duration = Column(String, nullable=True)
    steps = Column(Integer, nullable=True)
    calories = Column(Integer, nullable=True)
    date = Column(String, nullable=True)
    trainingPlanId = Column(Integer)

    def as_dict(self):
        return {
            "id": self.id,
            "userId": self.userId,
            "distance": self.distance,
            "duration": self.duration,
            "steps": self.steps,
            "calories": self.calories,
            "date": self.date.isoformat(),
            "trainingPlanId": self.trainingPlanId,
        }
