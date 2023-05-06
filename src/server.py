from fastapi import FastAPI
from controllers.trainings_controller import router as training_router


def init_routers(app):
    app.include_router(training_router, prefix="/api/trainings")


app = FastAPI()

init_routers(app)


@app.get("/")
async def index():
    return {"data": "test"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


