from datetime import datetime
from pydantic import BaseModel

class Product(BaseModel):
    datetimeObj: datetime
    date_str: str