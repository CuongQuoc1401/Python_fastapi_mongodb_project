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
        {"name": 1, "quantity_sold": 1, "_id": 0}  # Projection để lấy trường quantity_sold
    ).sort([("quantity_sold", -1)]).limit(10).to_list(length=None)

    return results

async def get_yesterday_best_selling_products(db: AsyncIOMotorClient, limit: int = 10):
    products_diff_collection = db["products_daily_diffs"]
    today = datetime.datetime.now().date()
    yesterday = today - datetime.timedelta(days=1)
    start_of_yesterday = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_of_yesterday = datetime.datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59, 999999)
    start_of_today = datetime.datetime(today.year, today.month, today.day, 0, 0, 0)
    end_of_today = datetime.datetime(today.year, today.month, today.day, 23, 59, 59, 999999)

    try:
        best_sellers_data = await products_diff_collection.find(
            {
                "snapshot_date": {"$gte": start_of_yesterday, "$lt": end_of_yesterday},
                "created_at": {"$gte": start_of_today, "$lte": end_of_today},
                "$expr": {"$gt": ["$quantity_sold_change", 0]} # Chỉ lấy sản phẩm có số lượng bán ra dương
            }
        ).sort([("quantity_sold_change", -1)]).limit(limit).to_list(length=None)

        # Convert ObjectId to string for JSON serialization
        best_sellers = []
        for item in best_sellers_data:
            item["_id"] = str(item["_id"])
            best_sellers.append(item)

        return best_sellers
    except Exception as e:
        print(f"Lỗi khi lấy sản phẩm bán chạy nhất ngày hôm qua: {e}")
        return []