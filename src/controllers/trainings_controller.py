
from constants import BLOCKED_STATE, ACTIVE_STATE
from services.metrics_service import send_system_metric
from services.user_service import check_if_user_exists_by_id, get_user_metadata
import requests
from fastapi import HTTPException
from model.training_request import AthleteGoalRequest, IntervalTrainingPlanRequest, IntervalUserTrainingRequest, TrainingPlanRequest, PlanReviewRequest, UserTrainingRequest
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Response, Depends, Header
from model.training import TrainingPlan
from db.database import training_dal
from firebase.firebaseUtils import upload_file
from fastapi import UploadFile, File
from fastapi.param_functions import File
from services.training_recomendation_service import recommend_trainings
from utils.age_calculator import calculate_age
import datetime
import random

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

    # add the multimedia to all trainings
    for training in result:
        training["multimedia"] = training_dal.get_training_images(
            training["id"])
        

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

    
    # add to the response the multimedia
    training_plan.multimedia = training_dal.get_training_images(
        training_plan.id)

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
            status_code=500, detail="Ya existe en favoritos. Recarga la lista")
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
            status_code=500, detail=f"No tienes al entrenamiento en favoritos. Recarga la lista")
    return JSONResponse(status_code=200, content=result.as_dict())


@router.get("/favorites/{user_id}")
async def get_favorite_trainings(user_id):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_favorite_trainings(user_id)
        for training in result:
            training["multimedia"] = training_dal.get_training_images(training["id"])
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
        latitude=request.latitude,
        longitude=request.longitude,
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
        latitude=training_request.latitude,
        longitude=training_request.longitude,
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


@router.put("/{training_plan_id}/image")
async def add_training_image(training_plan_id: int, file: UploadFile = File(...)):
    try:
        file_name = f"{file.filename}"
        url = upload_file(file.file, f"training_{training_plan_id}_{file_name}")
        result = training_dal.add_training_image(training_plan_id, url)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content={"message": "Image uploaded successfully download in: " + url})


@router.get("/{training_plan_id}/image")
async def get_training_image(training_plan_id: int):
    try:
        result = training_dal.get_training_images(training_plan_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)

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

@router.get("/user_training/{user_id}/count")
async def get_user_trainings_count(user_id: int):
    try:
        check_if_user_exists_by_id(user_id)
        result = training_dal.get_user_trainings_for_user_count(user_id)
        return JSONResponse(status_code=200, content=str(result))
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})

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



@router.post("/user_training/{user_id}/between_dates/group_by/{group_by}")
async def get_user_training_total_between_dates(user_id: int, group_by: str, request: IntervalUserTrainingRequest):
    try:
        check_if_user_exists_by_id(user_id)
        if group_by == "day" or group_by == "week" or group_by == "month" or group_by == "year":
            result = training_dal.get_user_training_total_between_dates_group_by(group_by, 
                user_id, request.start, request.end)
        else:
            raise HTTPException(status_code=400, detail="Invalid group by value")
        
        return JSONResponse(status_code=200, content=result)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})

def get_last_trainings(training_dal, user_id):
    last_user_trainings = training_dal.get_user_trainings(user_id)[:5]
    last_trainings = []
    for training in last_user_trainings:
        training_plan_id = int(training["id"])
        training_plan = training_dal.get_training_plan_by_id(training_plan_id).as_dict()
        last_trainings.append(training_plan)
    return last_trainings
    
def get_recommendations_response(training_dal, recommendations):
    print("Parsing recommendations dic!")
    '''
    Tenemos un diccionario de la forma:
    "types": arr[str]
    "difficulty": {"max: int, "min": int}
    "keywords": [str]
    '''
    recomendation_type = random.choice(recommendations["types"]) if len(recommendations["types"]) > 0 else "Running"
    min_difficulty = recommendations["difficulty"]["min"]
    max_difficulty = recommendations["difficulty"]["max"]
    print(f"Looking for trainings of type {recomendation_type} and difficulty from {min_difficulty} to {max_difficulty}")
    trainings = training_dal.get_trainings_within_filters(recomendation_type, min_difficulty, max_difficulty, recommendations["keywords"])
    return trainings


@router.get("/recommendation/{user_id}")
async def get_recommendations(user_id: int):
    try:
        user_metadata = get_user_metadata(user_id)
        
        if user_metadata is None:
            print(f"User {user_id} does not have metadata, using random data")
            age = 22
            weight_kg = 70
            height_cm = 170
            gender = "male"
            interests = ["cardio", "strength"]
            last_trainings = []
        else:
            print(f"Found metadata for user {user_id}")
            age = calculate_age(user_metadata["birthDate"])
            weight_kg = int(user_metadata["weight"])
            height_cm = int(user_metadata["height"])
            gender = "male"
            interests = user_metadata["interests"]
            last_trainings = get_last_trainings(training_dal, user_id)

        recommend_training_time = datetime.datetime.now()
        print(f"Calling recommend_trainings at {recommend_training_time.hour}:{recommend_training_time.minute}:{recommend_training_time.second}")
        trainings_response = recommend_trainings(age, weight_kg, height_cm, gender, interests, last_trainings)

        if trainings_response is None:
            return JSONResponse(status_code=500, content={"message": "Error in OpenAI api"})

        allowed_training_types = ["Running", "Swimming", "Biking", "Yoga", "Basketball", "Football", "Walking", "Gymnastics", "Dancing", "Hiking"]
        recommendation_types = []
        for t in trainings_response.types:
            if t in allowed_training_types:
                recommendation_types.append(t)

        response = {
            "types": recommendation_types,
            "difficulty": {
                "max": trainings_response.max_difficulty,
                "min": trainings_response.min_difficulty
            },
            "keywords": trainings_response.keywords
        }
        print("Got from gpt api: ")
        print(response)
        response_time = datetime.datetime.now()
        print(f"Sending response response at {response_time.hour}:{response_time.minute}:{response_time.second}")
        
        trainings = get_recommendations_response(training_dal, response)

        max_trainings = 10
        if len(trainings) < max_trainings:
            remaining = max_trainings - len(trainings)
            print(f"Only found {len(trainings)} trainings, looking for {remaining} more")
            more_trainings = training_dal.get_trainings_with_limit(remaining)
            print(f"Adding {len(more_trainings)} more trainings")
            trainings = trainings + more_trainings

            # add the multimedia to all trainings
        for training in trainings:
            training["multimedia"] = training_dal.get_training_images(training["id"])

        return JSONResponse(status_code=200, content=trainings)
    except Exception as e:
        print(f"Error in recommendations: {e}")
        try:
            trainings_failure = training_dal.get_trainings_with_limit(10)
            for t in trainings_failure:
                t["multimedia"] = training_dal.get_training_images(training["id"])

            return JSONResponse(status_code=200, content=trainings_failure)
        except Exception as e:
            return JSONResponse(status_code=500, content={"message": e})
    


@router.post("/goals/{athlete_id}")
async def add_athlete_goal(athlete_id: int, request: AthleteGoalRequest):
    try:
        result = training_dal.create_athlete_goal(request.title, request.description, request.type, request.metric, athlete_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result.as_dict())

@router.get("/goals/{athlete_id}")
async def get_athlete_goals(athlete_id: int):
    try:
        result = training_dal.get_athlete_goals(athlete_id)
            
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result)



@router.put("/goals/{goal_id}")
async def update_athlete_goal(goal_id: int, request: AthleteGoalRequest):
    try:
        result = training_dal.update_athlete_goal(goal_id, request.title, request.description, request.type, request.metric, request.achieved)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result.as_dict())

@router.delete("/goals/{goal_id}")
async def delete_athlete_goal(goal_id: int):
    try:
        training_dal.delete_athelete_goal(goal_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content={"message": "Goal deleted successfully"})


@router.post("/goals/{goal_id}/multimedia")
async def add_athlete_goal_image(goal_id: int, file: UploadFile = File(...)):
    try:        
        athlete_id = training_dal.get_athlete_goal_by_id(goal_id)["athleteId"]
        print(f"Uploading image for athlete {athlete_id}")
        file_name = f"{file.filename}"
        url = upload_file(file.file, f"goals/{athlete_id}/{file_name}")
        result = training_dal.add_multimedia_to_athlete_goal(goal_id, url)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content={"message": "Image uploaded successfully download in: " + url})

@router.put("/goals/{goal_id}/achieve")
async def achieve_athlete_goal(goal_id: int):
    try:
        result = training_dal.achieve_athlete_goal(goal_id)
    except HTTPException as e:
        return JSONResponse(status_code=e.status_code, content={"message": str(e.detail)})
    return JSONResponse(status_code=200, content=result.as_dict())