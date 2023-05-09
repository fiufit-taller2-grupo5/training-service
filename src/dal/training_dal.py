from sqlalchemy.orm import sessionmaker
from model.training import Training
from typing import List
from model.training import UserFavoriteTrainingPlan


class TrainingDal:

    def __init__(self, engine):
        self.engine = engine
        self.Session = sessionmaker(bind=self.engine)

    def get_training_by_id(self, training_id) -> Training | None:
        with self.Session() as session:
            return session.query(Training).filter(
                Training.id == training_id).first()

    def get_trainings(self, training_type: str | None, difficulty: str | None) -> List[Training] | None:
        with self.Session() as session:
            query = session.query(Training)
            if training_type is not None:
                query = query.filter(Training.type == training_type)
            if difficulty is not None:
                query = query.filter(Training.difficulty == difficulty)

            return query.all()

    def add_training(self, training: Training):
        with self.Session() as session:
            session.add(training)
            session.commit()
            session.refresh(training)
            return training

    def add_training_to_favorite(self, training_id: int, user_id: int):
        with self.Session() as session:
            user_favorite_training_plan = UserFavoriteTrainingPlan(
                userId=user_id, trainingPlanId=training_id)
            session.add(user_favorite_training_plan)
            session.commit()
            session.refresh(user_favorite_training_plan)
            return user_favorite_training_plan

    def get_favorite_trainings(self, user_id: int):
        with self.Session() as session:
            trainings = session.query(Training).join(UserFavoriteTrainingPlan, UserFavoriteTrainingPlan.trainingPlanId == Training.id) \
                .filter(UserFavoriteTrainingPlan.userId == user_id).all()
            return [training.as_dict() for training in trainings]
