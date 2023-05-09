from db.database import training_dal
from model.training import Training
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from model.training_request import TrainingRequest

router = APIRouter()
@router.get("/")
async def get_all_trainigs(response: Response, training_type: str = None, difficulty: int = None):
    result = training_dal.get_trainings(training_type, difficulty)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"message": "No trainings found"}
        )
    
    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    response.headers["X-Total-Count"] = str(len(result))
    
    return result


@router.get("/{training_id}")
async def get_training_by_id(training_id):
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

@router.get("/{training_id}/favorite/{user_id}")
async def add_training_to_favorite(training_id, user_id):
    result = training_dal.add_training_to_favorite(training_id, user_id)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"message": f"Training with id {training_id} does not exist"}
        )

    return JSONResponse(
        status_code=200,
        content=result
    )

@router.get("/favorites/{user_id}")
async def get_favorite_trainings(user_id):
    result = training_dal.get_favorite_trainings(user_id)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"message": f"User with id {user_id} does not exist"}
        )

    return JSONResponse(
        status_code=200,
        content=result
    )

@router.post("/")
async def add_training(training_request: TrainingRequest):
    training = Training(
        title=training_request.title,
        description=training_request.description,
        state=training_request.state,
        difficulty=training_request.difficulty,
        type=training_request.type,
        trainerId=training_request.trainerId,
    )
    result = training_dal.add_training(training)
    return JSONResponse(
        status_code=200,
        content=result.as_dict()
    )
