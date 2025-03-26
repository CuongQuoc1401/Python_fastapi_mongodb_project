from fastapi import APIRouter, HTTPException
from app.services.crawl_data_products_service import crawl_data_product_from_tiki

router = APIRouter()

@router.get("/crawl/data_product_from_tiki")
async def get_crawl_data_product_from_tiki():
    try:
        date_products = crawl_data_product_from_tiki()
        if not date_products:
            raise HTTPException(status_code=400, detail="No data found for the given date.")
        return date_products
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))