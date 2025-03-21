from datetime import datetime
from fastapi import FastAPI
from app.routes import user_routes
from app.routes import product_routes
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="My Awesome API",
    description="This is a description of my API",
    version="0.1.0",
)

origins = [
    "http://localhost:3000",  # Thay đổi cổng nếu trang web của bạn chạy trên cổng khác
    "http://127.0.0.1:3000",  # Thêm nếu bạn sử dụng 127.0.0.1
    "http://127.0.0.1:5500",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(product_routes.router)

