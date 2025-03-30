import time
from typing import Optional
import httpx  # Sử dụng httpx cho các request bất đồng bộ
from datetime import datetime, timedelta, timezone, time
from fastapi import Depends
from motor.motor_asyncio import AsyncIOMotorClient
from app.utils.database import get_database
import json
import asyncio

async def luu_du_lieu_san_pham_tiki_phan_trang(api_url: str, headers: dict, db: AsyncIOMotorClient):
    """Lấy dữ liệu từ API Tiki phân trang và lưu vào MongoDB (bất đồng bộ) bằng insert_many()."""
    collection = db["products"]
    page = 1  # Trang bắt đầu
    async with httpx.AsyncClient() as client:
        while True:
            current_url = f"{api_url}&page={page}"  # Thêm tham số trang vào URL
            try:
                response = await client.get(current_url, headers=headers)
                response.raise_for_status()
                data = response.json()

                if "data" in data and len(data["data"]) > 0:
                    products = data["data"]
                    products_to_insert = []
                    for product in products:
                        badges_text = [badge.get("text") for badge in product.get("badges_new", []) if badge.get("text")]
                        quantity_sold_data = product.get("quantity_sold")
                        quantity_sold_value: Optional[int] = None

                        if isinstance(quantity_sold_data, dict):
                            quantity_sold_value = quantity_sold_data.get("value")

                        try:
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
                                "quantity_sold": quantity_sold_value,  # Lưu trữ trực tiếp giá trị
                                "video_url": product.get("video_url"),
                                "origin": product.get("origin"),
                                "created_at": datetime.now(timezone.utc),
                                "updated_at": datetime.now(timezone.utc),
                                "ecommerce_name": "Tiki",
                            }
                            products_to_insert.append(product_data)
                        except Exception as e:
                            print(f"Lỗi khi tạo product_data cho product ID {product.get('id')}: {e}")

                    if products_to_insert:
                        try:
                            result = await collection.insert_many(products_to_insert)
                            # print(f"Đã chèn {len(result.inserted_ids)} bản ghi với IDs: {result.inserted_ids}")
                            print(f"Đã lưu dữ liệu trang {page}.")
                            await asyncio.sleep(0.5)  # Sử dụng asyncio.sleep cho bất đồng bộ
                            page += 1
                        except Exception as e:
                            print(f"Lỗi insert_many cho trang {page}: {e}")
                            break  # Dừng vòng lặp nếu có lỗi insert_many
                    else:
                        print("Không có sản phẩm nào để lưu ở trang này.")
                        break  # Dừng vòng lặp nếu không có sản phẩm
                else:
                    print("Không còn dữ liệu hoặc lỗi API.")
                    break  # Dừng vòng lặp nếu không còn dữ liệu hoặc lỗi API

            except httpx.RequestError as e:
                print(f"Lỗi kết nối API Tiki: {e}")
                break  # Dừng vòng lặp nếu có lỗi kết nối
            except httpx.HTTPStatusError as e:
                print(f"Lỗi HTTP API Tiki: {e}")
                break
            except Exception as e:
                print(f"Lỗi không xác định: {e}")
                break  # Dừng vòng lặp nếu có lỗi không xác định

    print("Hoàn tất quá trình lưu dữ liệu sản phẩm từ Tiki.")

async def loc_du_lieu_trung_lap(db: AsyncIOMotorClient):
    """Lọc dữ liệu trùng lặp trong bảng MongoDB (bất đồng bộ)."""
    collection = db["products"]
    ngay_hom_nay = datetime.now(timezone.utc).date()
    ngay_bat_dau = datetime.combine(ngay_hom_nay, time.min, tzinfo=timezone.utc)
    ngay_ket_thuc = datetime.combine(ngay_hom_nay, time.max, tzinfo=timezone.utc)

    cac_ban_ghi_hom_nay = collection.find({
        "created_at": {"$gte": ngay_bat_dau, "$lte": ngay_ket_thuc}
    })

    cac_ban_ghi_duy_nhat = {}
    async for ban_ghi in cac_ban_ghi_hom_nay:
        name = json.dumps(ban_ghi["name"]) if isinstance(ban_ghi["name"], dict) else ban_ghi["name"]
        url_key = json.dumps(ban_ghi["url_key"]) if isinstance(ban_ghi["url_key"], dict) else ban_ghi["url_key"]
        khoa = (name, url_key)

        if khoa not in cac_ban_ghi_duy_nhat:
            cac_ban_ghi_duy_nhat[khoa] = ban_ghi
        else:
            await collection.delete_one({"_id": ban_ghi["_id"]})
            print(f"Đã xóa bản ghi trùng lặp: {ban_ghi['_id']}")

    print("Lọc dữ liệu trùng lặp cho ngày hôm nay hoàn tất.")

async def xoa_du_lieu_theo_ngay(db: AsyncIOMotorClient):
    """Xóa các bản ghi trong MongoDB theo ngày created_at (bất đồng bộ)."""
    collection = db["products"]
    ngay_xoa = datetime.now(timezone.utc).date()
    ngay_bat_dau = datetime.combine(ngay_xoa, time.min, tzinfo=timezone.utc)
    ngay_ket_thuc = datetime.combine(ngay_xoa, time.max, tzinfo=timezone.utc)

    ket_qua = await collection.delete_many({
        "created_at": {
            "$gte": ngay_bat_dau,
            "$lte": ngay_ket_thuc
        }
    })
    print(f"Đã xóa {ket_qua.deleted_count} bản ghi của ngày {ngay_xoa}.")

async def crawl_data_product_from_tiki(db: AsyncIOMotorClient = Depends(get_database)):
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

    await xoa_du_lieu_theo_ngay(db)
    await luu_du_lieu_san_pham_tiki_phan_trang(api_url, headers, db)
    await loc_du_lieu_trung_lap(db)
    return "Success"