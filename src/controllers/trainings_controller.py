from db.database import training_dal
from model.training import Training
from fastapi import APIRouter, Response, Depends
from fastapi.responses import JSONResponse
from model.training_request import TrainingRequest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from constants import BLOCKED_STATE, ACTIVE_STATE
router = APIRouter()

def get_unblocked_training_plan(training_plan_id: int):
        # Initialize a new session
    training_plan = training_dal.get_training_by_id(training_plan_id)

    # If the training plan doesn't exist
    if not training_plan:
        raise HTTPException(status_code=404, detail="Training plan not found")

    # If the training plan is blocked
    if training_plan.state == BLOCKED_STATE:
        raise HTTPException(status_code=403, detail="Training plan is blocked")

    # If everything is okay, return the training plan
    return training_plan


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


@router.get("/{training_plan_id}")
async def get_training_by_id(training_plan: Training = Depends(get_unblocked_training_plan)):
    return JSONResponse(
        status_code=200,
        content=training_plan.as_dict()
    )


@router.post("/{training_plan_id}/favorite/{user_id}")
async def add_training_to_favorite(training_plan: Training = Depends(get_unblocked_training_plan), user_id: int = None):
    try:
        result = training_dal.add_training_to_favorite(training_plan.id, user_id)
    except:
        raise HTTPException(status_code=500, detail="Could not add to favorite")
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/favorites/{user_id}")
async def get_favorite_trainings(user_id):
    try:
        result = training_dal.get_favorite_trainings(user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)

@router.put("/{training_plan_id}/block")
async def block_training_plan(training_plan: Training = Depends(get_unblocked_training_plan)):
    training_plan.state = BLOCKED_STATE
    training_dal.update_training(training_plan)
    return JSONResponse(
        status_code=200,
        content=training_plan.as_dict()
    )

@router.put("/{training_plan_id}/unblock")
async def unblock_training_plan(training_plan_id):
    training_plan = training_dal.get_training_by_id(training_plan_id)

    # If the training plan doesn't exist
    if not training_plan:
        raise HTTPException(status_code=404, detail="Training plan not found")

    training_plan.state = ACTIVE_STATE
    training_dal.update_training(training_plan)

    return JSONResponse(
        status_code=200,
        content=training_plan.as_dict()
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
