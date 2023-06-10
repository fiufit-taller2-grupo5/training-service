from db.database import training_dal
from model.training import TrainingPlan
from fastapi import APIRouter, Request, Response, Depends, Header
from fastapi.responses import JSONResponse
from model.training_request import IntervalTrainingPlanRequest, IntervalUserTrainingRequest, TrainingPlanRequest, PlanReviewRequest, UserTrainingRequest
from fastapi import HTTPException
import requests
from services.user_service import check_if_user_exists_by_id
from services.metrics_service import send_system_metric

from constants import BLOCKED_STATE, ACTIVE_STATE
router = APIRouter()


def get_unblocked_training_plan(training_plan_id: int):
    # Initialize a new session
    training_plan = training_dal.get_training_plan_by_id(training_plan_id)

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
async def get_all_trainigs(response: Response, type: str = None, difficulty: int = None, trainer_id: int = None, x_role: str = Header(None)):
    print(f"X-Role: {x_role}")

    result = training_dal.get_trainings(
        type, difficulty, trainer_id, x_role == "user")

    headers = {"Access-Control-Expose-Headers": "X-Total-Count",
               "X-Total-Count": str(len(result))}
    result = [training.as_dict() for training in result]

    return JSONResponse(content=result, headers=headers)


@router.get("/between_dates_hours")
async def get_trainings_between_dates_and_hours(request: IntervalTrainingPlanRequest):
    try:
        result = training_dal.get_training_by_days_and_hours(
            request.days, request.start, request.end)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/between_hours")
async def get_trainings_between_hours(request: IntervalTrainingPlanRequest):
    try:
        result = training_dal.get_training_by_hours(
            request.start, request.end)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/between_dates")
async def get_trainings_between_dates(request: IntervalTrainingPlanRequest):
    try:
        result = training_dal.get_training_by_days(
            request.days)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/{training_plan_id}")
async def get_training_plan_by_id(training_plan_id: int, x_role: str = Header(None)):
    training_plan = training_dal.get_training_plan_by_id(
        training_plan_id, x_role == "user")

    if not training_plan:
        raise HTTPException(
            status_code=404, detail="Training plan not found")

    return JSONResponse(
        status_code=200,
        content=training_plan.as_dict()
    )


@router.post("/{training_plan_id}/favorite/{user_id}")
async def add_training_to_favorite(training_plan: TrainingPlan = Depends(get_unblocked_training_plan), user_id: int = None):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.add_training_to_favorite(
            training_plan.id, user_id)
    except:
        raise HTTPException(
            status_code=500, detail="Could not add to favorite")
    return JSONResponse(status_code=200, content=result.as_dict())


@router.delete("/{training_plan_id}")
async def delete_training(training_plan_id: int):
    training_dal.delete_training(training_plan_id)
    return JSONResponse(status_code=200, content={"message": "Training deleted successfully"})


@router.delete("/{training_plan_id}/favorite/{user_id}")
async def add_training_to_favorite(training_plan: TrainingPlan = Depends(get_unblocked_training_plan), user_id: int = None):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.delete_training_from_favorite(
            training_plan.id, user_id)
    except Exception as e:
        print(f"{e}")
        raise HTTPException(
            status_code=500, detail=f"Could not remove from favorites")
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/favorites/{user_id}")
async def get_favorite_trainings(user_id):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_favorite_trainings(user_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)


@router.put("/{training_plan_id}")
async def update_training(training_plan_id: int, request: TrainingPlanRequest, x_email: str = Header(None)):
    user_service_url = f"http://user-service:80/api/users/by_email/{x_email}"
    response = requests.get(user_service_url, headers={
        "test": "true",
        "dev": "true"})
    if response.status_code != 200:
        raise HTTPException(
            status_code=404, detail="Trainer not found")

    user = response.json()
    if user["role"] == "admin":
        training_plan = training_dal.get_training_plan_by_id(
            training_plan_id, False)
    else:
        training_plan = training_dal.get_training_plan_by_id(
            training_plan_id, True)

    if not training_plan:
        raise HTTPException(
            status_code=404, detail="Training plan not found")

    new_training_plan = TrainingPlan(
        id=training_plan_id,
        title=request.title,
        description=request.description,
        state=request.state,
        difficulty=request.difficulty,
        type=request.type,
        trainerId=request.trainerId,
        location=request.location,
        start=request.start,
        end=request.end,
        days=request.days
    )

    # training_plan.state = request.state
    updated = training_dal.update_training(new_training_plan)
    return JSONResponse(
        status_code=200,
        content=updated.as_dict()
    )


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
    training_plan = training_dal.get_training_plan_by_id(training_plan_id)

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
        location=training_request.location,
        start=training_request.start,
        end=training_request.end,
        days=training_request.days
    )
    try:
        result = training_dal.add_training(training)
        send_system_metric("training_plan_created")
        return JSONResponse(
            status_code=200,
            content=result.as_dict()
        )
    except HTTPException as e:
        return JSONResponse(
            status_code=e.status_code,
            content={
                "status": "error",
                "detail": f"{e.detail}"
            }
        )


@router.post("/{training_plan_id}/review/{user_id}")
async def add_training_review(training_plan_id: int, user_id: int, request: PlanReviewRequest):
    try:
        check_if_user_exists_by_id(user_id)
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


@router.post("/{training_plan_id}/user_training/{user_id}")
async def add_user_training(training_plan_id: int, user_id: int, request: UserTrainingRequest):
    try:
        check_if_user_exists_by_id(user_id)
        training_dal.get_training_plan_by_id(training_plan_id)
        result = training_dal.add_user_training(
            user_id, training_plan_id, request.distance, request.duration, request.steps, request.calories, request.date)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/{training_plan_id}/user_training/{user_id}")
async def get_user_trainings_of_training_plan(training_plan_id: int, user_id: int):
    try:
        check_if_user_exists_by_id(user_id)
        training_dal.get_training_plan_by_id(training_plan_id)
        result = training_dal.get_user_trainings_of_training_plan(
            user_id, training_plan_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)


@router.get("/user_training/{user_id}/average")
async def get_user_trainings_average(user_id: int):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_user_training_average(user_id)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/user_training/{user_id}/total")
async def get_user_trainings_total(user_id: int):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_user_training_total(user_id)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/user_training/{user_id}")
async def get_user_trainings(user_id: int):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_user_trainings(user_id)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/user_training/{user_id}/between_dates")
async def get_user_trainings_between_dates(user_id: int, request: IntervalUserTrainingRequest):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_user_trainings_between_dates(
            user_id, request.start, request.end)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})


@router.get("/user_training/{user_id}/between_dates/total")
async def get_user_training_total_between_dates(user_id: int, request: IntervalUserTrainingRequest):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_user_training_total_between_dates(
            user_id, request.start, request.end)
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
