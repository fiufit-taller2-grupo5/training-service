from sqlite3 import IntegrityError
from sqlalchemy.orm import sessionmaker
from model.training import Training
from typing import List
from model.training import UserFavoriteTrainingPlan, PlanReview
from fastapi import HTTPException
import requests
from constants import BLOCKED_STATE, ACTIVE_STATE
from sqlalchemy.exc import SQLAlchemyError


class TrainingDal:

    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_training_by_id(self, training_id) -> Training:
        with self.Session() as session:
            return session.query(Training).filter(
                Training.id == training_id).first()

    def get_trainings(self, training_type: str, difficulty: str, trainer_id: int, skip_blocked: bool = True) -> List[Training]:
        with self.Session() as session:
            query = session.query(Training)
            if training_type is not None:
                query = query.filter(Training.type == training_type)
            if difficulty is not None:
                query = query.filter(Training.difficulty == difficulty)
            if trainer_id is not None:
                query = query.filter(Training.trainerId == trainer_id)


            if skip_blocked:
                query = query.filter(Training.state == ACTIVE_STATE)
            return query.all()

    def add_training(self, training: Training):
        user_service_url = f"http://user-service:80/api/users/{training.trainerId}"
        response = requests.get(user_service_url)
        if response.status_code != 200:
            raise HTTPException(
                status_code=404, detail="Trainer not found")
        # check if the training.type is valid using the enum in the db
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

    def update_training(self, training: Training):
        with self.Session() as session:
            # Convert the Training object to a dictionary
            training_dict = training.__dict__
            # SQLAlchemy adds a '_sa_instance_state' key in the __dict__ method, you need to remove it
            training_dict.pop('_sa_instance_state', None)

            # Update the record
            session.query(Training).filter(
                Training.id == training.id).update(training_dict)
            session.commit()

            # Fetch the updated Training
            updated_training = session.query(Training).filter(
                Training.id == training.id).first()
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
                .filter(Training.state == ACTIVE_STATE).all()
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

                if session.query(Training).filter(Training.id == training_plan_id).count() == 0:
                    raise HTTPException(
                        status_code=404, detail="Training plan not found")

                user_service_url = f"http://user-service:80/api/users/{user_id}"
                response = requests.get(user_service_url)
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=404, detail="User not found")

                if session.query(PlanReview).filter(PlanReview.userId == user_id).filter(PlanReview.trainingPlanId == training_plan_id).count() > 0:
                    raise HTTPException(
                        status_code=408, detail="User already reviewed this training plan")

                training_plan = session.query(Training).filter(
                    Training.id == training_plan_id).first()
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
            if session.query(Training).filter(Training.id == training_plan_id).count() == 0:
                raise HTTPException(
                    status_code=404, detail="Training plan not found")
            reviews = session.query(PlanReview).filter(
                PlanReview.trainingPlanId == training_plan_id).all()
            if not reviews:
                return []
            return [review.as_dict() for review in reviews]
