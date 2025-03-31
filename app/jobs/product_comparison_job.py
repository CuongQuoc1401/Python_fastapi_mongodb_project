# app/jobs/product_comparison_job.py
from datetime import datetime, timedelta
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database

async def compare_daily_product_data(db: AsyncIOMotorClient = Depends(get_database)):
    products_collection = db["products"]
    products_diff_collection = db["products_daily_diffs"]

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    start_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59, 999999)
    start_today = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_today = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)

    print(f"Senior Dev Log (before find): Type of products_collection: {type(products_collection)}")
    yesterday_products = await products_collection.find(
        {"created_at": {"$gte": start_yesterday, "$lte": end_yesterday}}
    ).to_list(length=None)
    print(f"Senior Dev Log (after to_list): Type of yesterday_products: {type(yesterday_products)}")
    today_products = await products_collection.find(
        {"created_at": {"$gte": start_today, "$lte": end_today}}
    ).to_list(length=None)

    # Cần một cách hiệu quả để so sánh (ví dụ: index trên 'id')
    product_yesterday_map = {p.get("id"): p for p in yesterday_products}
    product_today_map = {p.get("id"): p for p in today_products}

    diffs_to_insert = []

    # Xóa tất cả dữ liệu diff của ngày hiện tại trước khi chèn
    deleted_result = await products_diff_collection.delete_many({
        "created_at": {"$gte": start_today, "$lte": end_today}
    })
    print(f"Senior Dev Log: Đã xóa {deleted_result.deleted_count} bản ghi diff của ngày {today}.")
    
    for product_id, today_product in product_today_map.items():
        yesterday_product = product_yesterday_map.get(product_id)
        changes = []
        yesterday_data = {}
        today_data = {}
        quantity_sold_change = None
        price_change = None

        if yesterday_product:
            yesterday_data["availability"] = yesterday_product.get("availability")
            yesterday_data["price"] = yesterday_product.get("price")
            yesterday_data["original_price"] = yesterday_product.get("original_price")
            yesterday_data["discount"] = yesterday_product.get("discount")
            yesterday_data["discount_rate"] = yesterday_product.get("discount_rate")
            yesterday_data["rating_average"] = yesterday_product.get("rating_average")
            yesterday_data["review_count"] = yesterday_product.get("review_count")
            yesterday_data["quantity_sold"] = yesterday_product.get("quantity_sold")

            today_data["availability"] = today_product.get("availability")
            today_data["price"] = today_product.get("price")
            today_data["original_price"] = today_product.get("original_price")
            today_data["discount"] = today_product.get("discount")
            today_data["discount_rate"] = today_product.get("discount_rate")
            today_data["rating_average"] = today_product.get("rating_average")
            today_data["review_count"] = today_product.get("review_count")
            today_data["quantity_sold"] = today_product.get("quantity_sold")

            if yesterday_data.get("availability") != today_data.get("availability"): changes.append("availability")
            if yesterday_data.get("price") != today_data.get("price"):
                changes.append("price")
                price_change = (today_data.get("price") or 0) - (yesterday_data.get("price") or 0)
            if yesterday_data.get("original_price") != today_data.get("original_price"): changes.append("original_price")
            if yesterday_data.get("discount") != today_data.get("discount"): changes.append("discount")
            if yesterday_data.get("discount_rate") != today_data.get("discount_rate"): changes.append("discount_rate")
            if yesterday_data.get("rating_average") != today_data.get("rating_average"): changes.append("rating_average")
            if yesterday_data.get("review_count") != today_data.get("review_count"): changes.append("review_count")
            if (yesterday_data.get("quantity_sold") or 0) != (today_data.get("quantity_sold") or 0):
                changes.append("quantity_sold")
                quantity_sold_change = (today_data.get("quantity_sold") or 0) - (yesterday_data.get("quantity_sold") or 0)
            else:
                quantity_sold_change = 0

            if changes:
                diffs_to_insert.append({
                    "product_id": today_product.get("id"),
                    "sku": today_product.get("sku"),
                    "name": today_product.get("name"),
                    "snapshot_date": datetime.combine(yesterday, datetime.min.time()),  # Convert to datetime
                    "data_yesterday": yesterday_data,
                    "data_today": today_data,
                    "changes": changes,
                    "quantity_sold_change": quantity_sold_change,  # Thêm trường này
                    "price_change": price_change,  # Thêm trường theo dõi thay đổi giá
                    "created_at": datetime.now(),
                    "updated_at": datetime.now(),
                    "ecommerce_name": today_product.get("ecommerce_name")
                })
        else:
            # Sản phẩm mới của ngày hôm nay
            diffs_to_insert.append({
                "product_id": today_product.get("id"),
                "sku": today_product.get("sku"),
                "name": today_product.get("name"),
                "snapshot_date": datetime.combine(today, datetime.min.time()),  # Convert to datetime
                "data_today": {
                    "availability": today_product.get("availability"),
                    "price": today_product.get("price"),
                    "original_price": today_product.get("original_price"),
                    "discount": today_product.get("discount"),
                    "discount_rate": today_product.get("discount_rate"),
                    "rating_average": today_product.get("rating_average"),
                    "review_count": today_product.get("review_count"),
                    "quantity_sold": today_product.get("quantity_sold")
                },
                "changes": ["new_product"],
                "quantity_sold_change": today_product.get("quantity_sold") or 0, # Số lượng bán ra kể từ khi xuất hiện
                "price_change": today_product.get("price") or 0, # Giá hiện tại của sản phẩm mới
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "ecommerce_name": today_product.get("ecommerce_name")
            })

    if diffs_to_insert:
        result = await products_diff_collection.insert_many(diffs_to_insert)
        print(f"Senior Dev Log: Đã chèn {len(result.inserted_ids)} bản ghi diff vào products_daily_diffs.")

    print(f"Senior Dev Log: Hoàn thành so sánh dữ liệu sản phẩm ngày {today}.")