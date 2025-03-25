from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.product_schema import Product
from app.services.product_service import best_seller_of_the_day
from app.services.token_service import get_current_user

router = APIRouter()

@router.get("/best_sellers/{date_str}")
async def get_best_sellers(date_str: str, username: str = Depends(get_current_user)):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        best_sellers = best_seller_of_the_day(date_obj)
        if not best_sellers:
            raise HTTPException(status_code=400, detail="No data found for the given date.")
        return best_sellers
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))