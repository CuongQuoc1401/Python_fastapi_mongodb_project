# app/jobs/product_comparison_job.py
from datetime import datetime, timedelta
from app.models.user_model import products_collection, products_diff_collection

async def compare_daily_product_data():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    start_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 0, 0, 0)
    end_yesterday = datetime(yesterday.year, yesterday.month, yesterday.day, 23, 59, 59, 999999)
    start_today = datetime(today.year, today.month, today.day, 0, 0, 0)
    end_today = datetime(today.year, today.month, today.day, 23, 59, 59, 999999)

    yesterday_products = await products_collection.find({"created_at": {"$gte": start_yesterday, "$lte": end_yesterday}}).to_list(length=None)
    today_products = await products_collection.find({"created_at": {"$gte": start_today, "$lte": end_today}}).to_list(length=None)

    # Cần một cách hiệu quả để so sánh (ví dụ: index trên 'id')
    product_yesterday_map = {p.get("id"): p for p in yesterday_products}
    product_today_map = {p.get("id"): p for p in today_products}

    for product_id, today_product in product_today_map.items():
        yesterday_product = product_yesterday_map.get(product_id)
        changes = []
        yesterday_data = {}
        today_data = {}

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

            if yesterday_data["availability"] != today_data["availability"]: changes.append("availability")
            if yesterday_data["price"] != today_data["price"]: changes.append("price")
            if yesterday_data["original_price"] != today_data["original_price"]: changes.append("original_price")
            if yesterday_data["discount"] != today_data["discount"]: changes.append("discount")
            if yesterday_data["discount_rate"] != today_data["discount_rate"]: changes.append("discount_rate")
            if yesterday_data["rating_average"] != today_data["rating_average"]: changes.append("rating_average")
            if yesterday_data["review_count"] != today_data["review_count"]: changes.append("review_count")
            if yesterday_data["quantity_sold"] != today_data["quantity_sold"]: changes.append("quantity_sold")

            await products_diff_collection.insert_one({
                "product_id": today_product.get("id"),
                "sku": today_product.get("sku"),
                "name": today_product.get("name"),
                "snapshot_date": yesterday,
                "data_yesterday": yesterday_data,
                "data_today": today_data,
                "changes": changes,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "ecommerce_name": today_product.get("ecommerce_name")
            })
        else:
            # Sản phẩm mới của ngày hôm nay
            await products_diff_collection.insert_one({
                "product_id": today_product.get("id"),
                "sku": today_product.get("sku"),
                "name": today_product.get("name"),
                "snapshot_date": today,
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
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
                "ecommerce_name": today_product.get("ecommerce_name")
            })

    print(f"Senior Dev Log: Hoàn thành so sánh dữ liệu sản phẩm ngày {today}.")