from fastapi import FastAPI
from controllers.trainings_controller import router as training_router
import uvicorn


def init_routers(app):
    app.include_router(training_router, prefix="/api/trainings")


app = FastAPI()

init_routers(app)
print("Hello form root")


@app.get("/")
def index():
    return {"data": "test"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app)
