from fastapi import FastAPI
from controllers.trainings_controller import router as training_router
from starlette.middleware.cors import CORSMiddleware


def init_routers(app):
    app.include_router(training_router, prefix="/api/trainings")


app = FastAPI()

origins = [
    "http://localhost:80",  # adjust this as necessary
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count"]  # expose your custom header
)

init_routers(app)


@app.get("/")
async def index():
    return {"data": "test"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}


