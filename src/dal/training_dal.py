from sqlite3 import IntegrityError
from sqlalchemy.orm import sessionmaker
from model.training import Training
from typing import List
from model.training import UserFavoriteTrainingPlan
from fastapi import HTTPException
import requests
from constants import BLOCKED_STATE, ACTIVE_STATE



class TrainingDal:

    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_training_by_id(self, training_id) -> Training:
        with self.Session() as session:
            return session.query(Training).filter(
                Training.id == training_id).first()

    def get_trainings(self, training_type: str, difficulty: str, skip_blocked: bool = True) -> List[Training]:
        with self.Session() as session:
            query = session.query(Training)
            if training_type is not None:
                query = query.filter(Training.type == training_type)
            if difficulty is not None:
                query = query.filter(Training.difficulty == difficulty)

            if skip_blocked:
                query = query.filter(Training.state == ACTIVE_STATE)
            return query.all()

    def add_training(self, training: Training):
        user_service_url = f"http://user-service:80/api/users/{training.trainerId}"
        response = requests.get(user_service_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail="User not found")

        with self.Session() as session:
            session.add(training)
            session.commit()
            session.refresh(training)
            return training
    def update_training(self, training: Training):
        with self.Session() as session:
            # Convert the Training object to a dictionary
            training_dict = training.__dict__
            # SQLAlchemy adds a '_sa_instance_state' key in the __dict__ method, you need to remove it
            training_dict.pop('_sa_instance_state', None)

            # Update the record
            session.query(Training).filter(Training.id == training.id).update(training_dict)
            session.commit()

            # Fetch the updated Training
            updated_training = session.query(Training).filter(Training.id == training.id).first()
            return updated_training


    def add_training_to_favorite(self, training_id: int, user_id: int):
        with self.Session() as session:
            try:
                user_favorite_training_plan = UserFavoriteTrainingPlan(
                    userId=user_id, trainingPlanId=training_id)
                session.add(user_favorite_training_plan)
                session.commit()
                session.refresh(user_favorite_training_plan)
                return user_favorite_training_plan
            except IntegrityError:
                session.rollback()
                raise HTTPException(
                    status_code=404, detail="User or training not found")
            except:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail="Something went wrong")

    def get_favorite_trainings(self, user_id: int):
        with self.Session() as session:
            trainings = session.query(Training).join(UserFavoriteTrainingPlan, UserFavoriteTrainingPlan.trainingPlanId == Training.id) \
                .filter(UserFavoriteTrainingPlan.userId == user_id) \
                .filter(Training.state is ACTIVE_STATE).all()
            if not trainings:
                return []
            return [training.as_dict() for training in trainings]
