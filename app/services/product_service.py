import datetime
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database

async def best_seller_of_shop(datetimeObj: datetime.datetime, db: AsyncIOMotorClient = Depends(get_database)):
    if datetimeObj < datetime.datetime(2025, 3, 21) or datetimeObj >= datetime.datetime.now():
        return "Data Not Found"

    start_of_day = datetimeObj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = datetimeObj.replace(hour=23, minute=59, second=59, microsecond=999999)

    results = await db["products"].find(
        {"created_at": {"$gte": start_of_day, "$lte": end_of_day}},
        {"name": 1, "quantity_sold.value": 1, "_id": 0}  # Projection
    ).sort([("quantity_sold.value", -1)]).limit(10).to_list(length=None)

    return results