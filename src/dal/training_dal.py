from sqlalchemy.orm import sessionmaker
from model.training import Training
from typing import List


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
            # return session.query(Training).all()
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
