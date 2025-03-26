import time
import requests
import pymongo
from datetime import datetime, timedelta
from app.models.user_model import products_collection
import json
# import datetime

def luu_du_lieu_san_pham_tiki_phan_trang(api_url, headers, collection):
    """Lấy dữ liệu từ API Tiki phân trang và lưu vào MongoDB."""
    page = 1  # Trang bắt đầu
    while True:
        current_url = f"{api_url}&page={page}"  # Thêm tham số trang vào URL
        try:
            response = requests.get(current_url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if "data" in data and len(data["data"]) > 0:
                products = data["data"]
                for product in products:
                    badges_text = [badge.get("text") for badge in product.get("badges_new", []) if badge.get("text")]
                    product_data = {
                        "id": product.get("id"),
                        "sku": product.get("sku"),
                        "name": product.get("name"),
                        "url_key": product.get("url_key"),
                        "url_path": product.get("url_path"),
                        "availability": product.get("availability"),
                        "seller_id": product.get("seller_id"),
                        "seller_name": product.get("seller_name"),
                        "brand_id": product.get("brand_id"),
                        "brand_name": product.get("brand_name"),
                        "price": product.get("price"),
                        "original_price": product.get("original_price"),
                        "badges_new": badges_text,
                        "discount": product.get("discount"),
                        "discount_rate": product.get("discount_rate"),
                        "rating_average": product.get("rating_average"),
                        "review_count": product.get("review_count"),
                        "category_ids": product.get("category_ids"),
                        "primary_category_path": product.get("primary_category_path"),
                        "primary_category_name": product.get("primary_category_name"),
                        "thumbnail_url": product.get("thumbnail_url"),
                        "quantity_sold": product.get("quantity_sold"),
                        "video_url": product.get("video_url"),
                        "origin": product.get("origin"),
                        "created_at": datetime.now(),
                        "updated_at": datetime.now(),
                        "ecommerce_name": "Tiki",
                    }
                    collection.insert_one(product_data)
                print(f"Đã lưu dữ liệu trang {page}.")
                time.sleep(1)
                page += 1
            else:
                print("Không còn dữ liệu hoặc lỗi API.")
                break  # Dừng vòng lặp nếu không còn dữ liệu hoặc lỗi API

        except requests.exceptions.RequestException as e:
            print(f"Lỗi kết nối API Tiki: {e}")
            break  # Dừng vòng lặp nếu có lỗi kết nối
        except Exception as e:
            print(f"Lỗi không xác định: {e}")
            break  # Dừng vòng lặp nếu có lỗi không xác định

def loc_du_lieu_trung_lap(collection):
    """Lọc dữ liệu trùng lặp trong bảng MongoDB."""

    # ngay_hom_nay = datetime(2025, 3,21)
    ngay_hom_nay = datetime.now().date()
    ngay_bat_dau = datetime.combine(ngay_hom_nay, datetime.min.time())
    ngay_ket_thuc = datetime.combine(ngay_hom_nay, datetime.max.time())

    cac_ban_ghi_hom_nay = collection.find({
        "created_at": {"$gte": ngay_bat_dau, "$lte": ngay_ket_thuc}
    })

    cac_ban_ghi_duy_nhat = {}

    for ban_ghi in cac_ban_ghi_hom_nay:
        # Kiểm tra xem các trường có phải là dictionary không và chuyển đổi chúng thành chuỗi nếu cần
        name = json.dumps(ban_ghi["name"]) if isinstance(ban_ghi["name"], dict) else ban_ghi["name"]
        # price = json.dumps(ban_ghi["price"]) if isinstance(ban_ghi["price"], dict) else ban_ghi["price"]
        # quantity_sold = json.dumps(ban_ghi["quantity_sold"]) if isinstance(ban_ghi["quantity_sold"], dict) else ban_ghi["quantity_sold"]
        url_key = json.dumps(ban_ghi["url_key"]) if isinstance(ban_ghi["url_key"], dict) else ban_ghi["url_key"]

        khoa = (name, url_key)

        if khoa not in cac_ban_ghi_duy_nhat:
            cac_ban_ghi_duy_nhat[khoa] = ban_ghi
        else:
            collection.delete_one({"_id": ban_ghi["_id"]})
            print(f"Đã xóa bản ghi trùng lặp: {ban_ghi['_id']}")

    print("Lọc dữ liệu trùng lặp cho ngày hôm nay hoàn tất.")
    
def xoa_du_lieu_theo_ngay(collection):
    """Xóa các bản ghi trong MongoDB theo ngày created_at."""

    ngay_xoa = datetime.now().date()
    ngay_bat_dau = datetime.combine(ngay_xoa, datetime.min.time())
    ngay_ket_thuc = datetime.combine(ngay_xoa, datetime.max.time())

    ket_qua = collection.delete_many({
        "created_at": {
            "$gte": ngay_bat_dau,
            "$lte": ngay_ket_thuc
        }
    })
    
collection = products_collection

# Thông tin API Tiki (CẦN CẬP NHẬT)
api_url = "https://tiki.vn/api/v2/products?limit=40&include=advertisement&aggregations=2&trackity_id=fcc6affa-3f44-8396-fcd9-1f635bd03925&q=samsung"
headers = {
    "authority": "tiki.vn",
    "method": "GET",
    "path": "/api/v2/products?limit=40&include=advertisement&aggregations=2&trackity_id=fcc6affa-3f44-8396-fcd9-1f635bd03925&q=samsung",
    "scheme": "https",
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5",
    "Cookie": "_trackity=fcc6affa-3f44-8396-fcd9-1f635bd03925; tiki_client_id=gd_au=1.1.728590450.1742535524",
    "Referer": "https://tiki.vn/search?q=samsung",
    "Sec-Ch-Ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
    "X-Guest-Token": "InWjvpfZmChXUzr7PARVSQFaJcLbG9Eu"
}

# Gọi hàm để lưu dữ liệu Tiki phân trang
# xoa_du_lieu_theo_ngay(collection)
# luu_du_lieu_san_pham_tiki_phan_trang(api_url, headers, collection)
# loc_du_lieu_trung_lap(collection)

def crawl_data_product_from_tiki(api_url, headers, collection):
    xoa_du_lieu_theo_ngay(collection)
    luu_du_lieu_san_pham_tiki_phan_trang(api_url, headers, collection)
    loc_du_lieu_trung_lap(collection)