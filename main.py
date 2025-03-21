from datetime import datetime
from fastapi import FastAPI
from app.routes import user_routes
from app.routes import product_routes
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.api_model import APIModel
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter

load_dotenv()

app = FastAPI(
    title="My Awesome API",
    description="This is a description of my API",
    version="0.1.0",
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = InferringRouter()  # Tạo InferringRouter

@cbv(router)
class MyAwesomeAPI:
    @router.get("/")
    def read_root(self):
        return {"message": "Hello, World!"}

app.include_router(router)  # Include InferringRouter

app.include_router(user_routes.router)
app.include_router(product_routes.router)