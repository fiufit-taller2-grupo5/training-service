from db.database import training_dal
from model.training import Training
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from model.training_request import TrainingRequest
from fastapi import HTTPException

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


@router.post("/{training_id}/favorite/{user_id}")
async def add_training_to_favorite(training_id, user_id):
    try:
        result = training_dal.add_training_to_favorite(training_id, user_id)
    except:
        return JSONResponse(status_code=result, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/favorites/{user_id}")
async def get_favorite_trainings(user_id):
    try:
        result = training_dal.get_favorite_trainings(user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)


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
