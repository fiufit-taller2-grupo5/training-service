from ast import FunctionDef
from decimal import Decimal
from sqlite3 import IntegrityError
from sqlalchemy.orm import sessionmaker
from model.training import TrainingPlan
from typing import List
from model.training import UserFavoriteTrainingPlan, PlanReview, UserTraining
from fastapi import HTTPException
import requests
from constants import BLOCKED_STATE, ACTIVE_STATE
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import func


class TrainingDal:

    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_training_by_id(self, training_id, skip_blocked: bool = True) -> TrainingPlan:
        with self.Session() as session:
            if skip_blocked:
                return session.query(TrainingPlan).filter(
                    TrainingPlan.id == training_id).filter(
                    TrainingPlan.state == ACTIVE_STATE).first()
            else:
                return session.query(TrainingPlan).filter(
                TrainingPlan.id == training_id).first()

    def get_trainings(self, training_type: str, difficulty: str, trainer_id: int, skip_blocked: bool = True) -> List[TrainingPlan]:
        with self.Session() as session:
            try: 
                query = session.query(TrainingPlan)
                if training_type is not None:
                    query = query.filter(TrainingPlan.type == training_type)
                if difficulty is not None:
                    query = query.filter(TrainingPlan.difficulty == difficulty)
                if trainer_id is not None:
                    query = query.filter(TrainingPlan.trainerId == trainer_id)

                if skip_blocked:
                    query = query.filter(TrainingPlan.state == ACTIVE_STATE)
                return query.all()
            except SQLAlchemyError as e:
                return []

    def add_training(self, training: TrainingPlan):
        try:
            with self.Session() as session:
                session.add(training)
                session.commit()
                session.refresh(training)
                return training
        except IntegrityError as e:
            session.rollback()
            raise HTTPException(
                status_code=500, detail=e.args[0])

    def update_training(self, training: TrainingPlan):
        with self.Session() as session:
            # Convert the TrainingPlan object to a dictionary
            training_dict = training.__dict__
            # SQLAlchemy adds a '_sa_instance_state' key in the __dict__ method, you need to remove it
            training_dict.pop('_sa_instance_state', None)

            # Update the record
            session.query(TrainingPlan).filter(
                TrainingPlan.id == training.id).update(training_dict)
            session.commit()

            # Fetch the updated TrainingPlan
            updated_training = session.query(TrainingPlan).filter(
                TrainingPlan.id == training.id).first()
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
            trainings = session.query(TrainingPlan).join(UserFavoriteTrainingPlan, UserFavoriteTrainingPlan.trainingPlanId == TrainingPlan.id) \
                .filter(UserFavoriteTrainingPlan.userId == user_id) \
                .filter(TrainingPlan.state == ACTIVE_STATE).all()
            if not trainings:
                return []
            return [training.as_dict() for training in trainings]

    def add_training_review(self, training_plan_id: int, user_id: int, score: int, comment: str = None):
        with self.Session() as session:
            try:

                if not user_id or not training_plan_id or not score:
                    raise HTTPException(
                        status_code=400, detail="Missing required fields (user_id, training_plan_id or score))")

                if score < 1 or score > 5:
                    raise HTTPException(
                        status_code=400, detail="Score must be between 1 and 5")

                if session.query(TrainingPlan).filter(TrainingPlan.id == training_plan_id).count() == 0:
                    raise HTTPException(
                        status_code=404, detail="Training plan not found")

                user_service_url = f"http://user-service:80/api/users/{user_id}"
                response = requests.get(user_service_url, headers={
                                "test": "true",
                                "dev": "true"})

                if response.status_code != 200:
                    raise HTTPException(
                        status_code=404, detail="User not found")

                if session.query(PlanReview).filter(PlanReview.userId == user_id).filter(PlanReview.trainingPlanId == training_plan_id).count() > 0:
                    raise HTTPException(
                        status_code=408, detail="User already reviewed this training plan")

                training_plan = session.query(TrainingPlan).filter(
                    TrainingPlan.id == training_plan_id).first()
                if training_plan.trainerId == user_id:
                    raise HTTPException(
                        status_code=409, detail="Trainer can't review his own training plan")

                training_review = PlanReview(
                    userId=user_id, score=score, comment=comment, trainingPlanId=training_plan_id)
                session.add(training_review)
                session.commit()
                session.refresh(training_review)
                return training_review
            except HTTPException as e:
                session.rollback()
                raise HTTPException(
                    status_code=e.status_code, detail=e.detail)
            except:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail="Something went wrong")

    def get_training_reviews(self, training_plan_id: int):
        with self.Session() as session:
            if session.query(TrainingPlan).filter(TrainingPlan.id == training_plan_id).count() == 0:
                raise HTTPException(
                    status_code=404, detail="Training plan not found")
            reviews = session.query(PlanReview).filter(
                PlanReview.trainingPlanId == training_plan_id).all()
            if not reviews:
                return []
            return [review.as_dict() for review in reviews]

    def add_user_training(self, user_id: int, training_plan_id: int, distance: float, duration: float, steps: int, calories: int, date: str):
        with self.Session() as session:
            try:
                if not distance or not duration or not steps or not calories or not date:
                    raise HTTPException(
                        status_code=400, detail="Missing required fields (distance, duration, steps, calories or date)")

                if distance < 0 or duration < 0 or steps < 0 or calories < 0:
                    raise HTTPException(
                        status_code=400, detail="Distance, duration, steps and calories must be positive")

                user_training = UserTraining(userId=user_id, trainingPlanId=training_plan_id,
                                             distance=distance, duration=duration, steps=steps, calories=calories, date=date)
                session.add(user_training)
                session.commit()
                session.refresh(user_training)
                return user_training
            except HTTPException as e:
                session.rollback()
                raise HTTPException(
                    status_code=e.status_code, detail=e.detail)
            except Exception as e:
                session.rollback()
                raise HTTPException(
                    status_code=500, detail=f"Something went wrong: {e}")

    def get_user_training_average(self, user_id: int):
        with self.Session() as session:
            user_service_url = f"http://user-service:80/api/users/{user_id}"
            response = requests.get(user_service_url, headers={
                                "test": "true",
                                "dev": "true"})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404, detail="User not found")

            user_training_query = session.query(
                func.avg(UserTraining.distance),
                func.avg(UserTraining.duration),
                func.avg(UserTraining.steps),
                func.avg(UserTraining.calories)
            ).filter(UserTraining.userId == user_id)

            user_training_averages = user_training_query.first()

            if not user_training_averages[0]:
                return {
                    "distance": 0,
                    "duration": 0,
                    "steps": 0,
                    "calories": 0
                }

            return {
                "distance": float(user_training_averages[0]),
                "duration": float(user_training_averages[1]),
                "steps": float(user_training_averages[2]),
                "calories": float(user_training_averages[3])
            }

    def get_user_training_total(self, user_id: int):
        with self.Session() as session:
            user_service_url = f"http://user-service:80/api/users/{user_id}"
            response = requests.get(user_service_url, headers={
                                "test": "true",
                                "dev": "true"})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404, detail="User not found")

            user_training_query = session.query(
                func.sum(UserTraining.distance),
                func.sum(UserTraining.duration),
                func.sum(UserTraining.steps),
                func.sum(UserTraining.calories)
            ).filter(UserTraining.userId == user_id)

            user_training_totals = user_training_query.first()

            if not user_training_totals[0]:
                return {
                    "distance": 0,
                    "duration": 0,
                    "steps": 0,
                    "calories": 0
                }

            return {
                "distance": float(user_training_totals[0]),
                "duration": float(user_training_totals[1]),
                "steps": float(user_training_totals[2]),
                "calories": float(user_training_totals[3])
            }

    def get_user_trainings(self, user_id: int):
        with self.Session() as session:
            user_service_url = f"http://user-service:80/api/users/{user_id}"
            response = requests.get(user_service_url, headers={
                                "test": "true",
                                "dev": "true"})
            if response.status_code != 200:
                raise HTTPException(
                    status_code=404, detail="User not found")

            user_trainings = session.query(UserTraining).filter(
                UserTraining.userId == user_id).all()
            if not user_trainings:
                return []
            return [training.as_dict() for training in user_trainings]
