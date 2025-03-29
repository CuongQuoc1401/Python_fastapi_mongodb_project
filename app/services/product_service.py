import datetime
from xmlrpc import client
from app.models.user_model import products_collection
from app.utils.database import client

def best_seller_of_shop(datetimeObj):
    if datetimeObj < datetime.datetime(2025, 3, 21) or datetimeObj >= datetime.datetime.now():
        return "Data Not Found"
    
    start_of_day = datetimeObj.replace(hour=0, minute=0, second=0, microsecond=0)
    end_of_day = datetimeObj.replace(hour=23, minute=59, second=59, microsecond=999999)
    results = list(products_collection.find(
    {"created_at": {"$gte": start_of_day, "$lte": end_of_day}},
    {"name": 1, "quantity_sold.value": 1, "_id": 0}  # Projection
).sort([("quantity_sold.value", -1)]).limit(10))

    return results
   