from sqlalchemy import create_engine
from dal.training_dal import TrainingDal

host = "localhost"
port = "8888"
db_name = "postgres"
schema = "training-service"
user = "postgres"
password = "12345678"
uri = f"postgresql://{user}:{password}@{host}:{port}/{db_name}"

print(f"Connecting to {uri}")

engine = create_engine(
    uri, connect_args={"options": f"-csearch_path={schema}"}
)

print("Conected to database")

training_dal = TrainingDal(engine)
