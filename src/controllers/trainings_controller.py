from db.database import training_dal
from model.training import TrainingPlan
from fastapi import APIRouter, Request, Response, Depends
from fastapi.responses import JSONResponse
from model.training_request import TrainingPlanRequest, PlanReviewRequest, UserTrainingRequest
from fastapi import HTTPException
from sqlalchemy.orm import sessionmaker
from constants import BLOCKED_STATE, ACTIVE_STATE
router = APIRouter()


def get_unblocked_training_plan(training_plan_id: int):
    # Initialize a new session
    training_plan = training_dal.get_training_by_id(training_plan_id)

    if not training_plan:
        raise HTTPException(
            status_code=404,
            detail=f"Training with id {training_plan_id} does not exist"
        )

    if training_plan.state == BLOCKED_STATE:
        raise HTTPException(
            status_code=404,
            detail=f"Training with id {training_plan_id} is blocked"
        )

    return training_plan


@router.get("/")
async def get_all_trainigs(response: Response, training_type: str = None, difficulty: int = None, trainer_id: int = None, skip_blocked: bool = True):
    result = training_dal.get_trainings(
        training_type, difficulty, trainer_id, skip_blocked)
    if result is None:
        return JSONResponse(
            status_code=404,
            content={"message": "No trainings found"}
        )

    response.headers["Access-Control-Expose-Headers"] = "X-Total-Count"
    response.headers["X-Total-Count"] = str(len(result))

    return result


@router.get("/{training_plan_id}")
async def get_training_by_id(training_plan: TrainingPlan = Depends(get_unblocked_training_plan)):
    return JSONResponse(
        status_code=200,
        content=training_plan.as_dict()
    )


@router.post("/{training_plan_id}/favorite/{user_id}")
async def add_training_to_favorite(training_plan: TrainingPlan = Depends(get_unblocked_training_plan), user_id: int = None):
    try:
        result = training_dal.add_training_to_favorite(
            training_plan.id, user_id)
    except:
        raise HTTPException(
            status_code=500, detail="Could not add to favorite")
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/favorites/{user_id}")
async def get_favorite_trainings(user_id):
    try:
        result = training_dal.get_favorite_trainings(user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)


@router.put("/{training_plan_id}/block")
async def block_training_plan(training_plan: TrainingPlan = Depends(get_unblocked_training_plan)):
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
        raise HTTPException(
            status_code=404, detail="Training plan not found")

    training_plan.state = ACTIVE_STATE
    training_dal.update_training(training_plan)

    return JSONResponse(
        status_code=200,
        content=training_plan.as_dict()
    )


@router.post("/")
async def add_training(training_request: TrainingPlanRequest):
    training = TrainingPlan(
        title=training_request.title,
        description=training_request.description,
        state=training_request.state,
        difficulty=training_request.difficulty,
        type=training_request.type,
        trainerId=training_request.trainerId,
    )
    try:
        result = training_dal.add_training(training)
        return JSONResponse(
            status_code=200,
            content=result.as_dict()
        )
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={
                "status": "error",
                "message": "Could not add training, maybe there's a missing property",
                "fullMessage": f"{e}"
            }
        )


@router.post("/{training_plan_id}/review/{user_id}")
async def add_training_review(training_plan_id: int, user_id: int, request: PlanReviewRequest):
    try:
        result = training_dal.add_training_review(
            training_plan_id, user_id, request.score, str(request.comment))
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/{training_plan_id}/reviews")
async def get_training_reviews(training_plan_id: int):
    try:
        result = training_dal.get_training_reviews(training_plan_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)


@router.post("/user_training/{user_id}")
async def add_user_training(user_id: int, request: UserTrainingRequest):
    try:
        result = training_dal.add_user_training(
            user_id, request.trainingPlanId, request.distance, request.duration, request.steps, request.calories, request.date)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/user_training/{user_id}/average")
async def get_user_trainings(user_id: int):
    try:
        result = training_dal.get_user_training_average(user_id)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/user_training/{user_id}/total")
async def get_user_trainings(user_id: int):
    try:
        result = training_dal.get_user_training_total(user_id)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/user_training/{user_id}")
async def get_user_trainings(user_id: int):
    try:
        result = training_dal.get_user_trainings(user_id)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
