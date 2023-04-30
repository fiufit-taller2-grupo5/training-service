from db.database import training_dal
from model.training import Training
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from model.training_request import TrainingRequest

router = APIRouter()


@router.get("/")
def get_all_trainigs(training_type: str = None, difficulty: int = None):
    result = training_dal.get_trainings(training_type, difficulty)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"message": "No trainings found"}
        )

    return result


@router.get("/{training_id}")
def get_training_by_id(training_id):
    result = training_dal.get_training_by_id(training_id)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"message": f"Training with id {training_id} does not exist"}
        )

    return JSONResponse(
        status_code=200,
        content=result.as_dict()
    )


@router.post("/")
def add_training(training_request: TrainingRequest):
    training = Training(
        title=training_request.title,
        description=training_request.description,
        multimedia=training_request.multimedia,
        state=training_request.state,
        difficulty=training_request.difficulty,
        type=training_request.type,
        trainer_id=training_request.trainer_id,
        multimedia_id=training_request.multimedia_id
    )
    result = training_dal.add_training(training)
    return JSONResponse(
        status_code=200,
        content=result.as_dict()
    )
