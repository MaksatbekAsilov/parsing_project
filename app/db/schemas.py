from pydantic import BaseModel
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class CryptoPrice(BaseModel):
    currency: str
    price: float
    timestamp: datetime

class PriceStats(BaseModel):
    min_price: float
    max_price: float

class UserLogin(BaseModel):
    email: str
    password: str

class ConvertRequest(BaseModel):
    from_currency: str
    to_currency: str
    source: str
    amount: float
   