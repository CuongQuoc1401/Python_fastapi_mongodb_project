from datetime import datetime
from fastapi import FastAPI
from app.routes import user_routes, product_routes
from app.routes import crawl_data_products_routes
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from app.schedules.scheduler import start_scheduler, stop_scheduler

load_dotenv()

app = FastAPI(
    title="My Awesome API",
    description="This is a description of my API",
    version="0.1.0",
)

# origins = [
#     "http://localhost:3000",  # Thay đổi cổng nếu trang web của bạn chạy trên cổng khác
#     "http://127.0.0.1:3000",  # Thêm nếu bạn sử dụng 127.0.0.1
#     "http://127.0.0.1:5500",  
# ]
origins = ["*"]
# origins = ["http://localhost:3000", "https://abc-domain.com"]
# origins=["http://fe-statistic-app-debug-git-master-cuongquoc1401-projects.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_routes.router)
app.include_router(product_routes.router)
app.include_router(crawl_data_products_routes.router)

##job
@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()

@app.get("/read_root")
def read_root():
    return {"message": "Hello, World!"}

