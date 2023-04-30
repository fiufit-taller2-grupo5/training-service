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

    def get_all_trainings(self) -> List[Training] | None:
        with self.Session() as session:
            return session.query(Training).all()
