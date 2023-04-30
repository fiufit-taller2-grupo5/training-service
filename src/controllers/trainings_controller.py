from http.client import HTTPException
from db.database import training_dal
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
def get_all_trainigs():
    result = training_dal.get_all_trainings()
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
