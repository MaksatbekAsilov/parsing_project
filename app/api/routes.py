# from fastapi import APIRouter, HTTPException, Depends, Body, Query
# from sqlalchemy.orm import Session
# from typing import List, Optional

# from app.api import crud
# from app.schemas import schemas
# from app.service.utils import verify_token
# from fastapi.security import OAuth2PasswordBearer

# router = APIRouter()
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# @router.post("/convert")
# def convert_currency_endpoint(request: schemas.ConvertRequest, db: Session = Depends(crud.get_db)):
#     if not request.source:
#         raise HTTPException(status_code=400, detail="Source is required")
    
#     result = crud.convert_currency(db, request.from_currency, request.to_currency, request.amount, request.source)
#     return result

# @router.get("/dashboard")
# def get_dashboard(token: str = Depends(oauth2_scheme)):
#     try:
#         user = verify_token(token)
#         return {"message": "Welcome to your dashboard!", "user_email": user["sub"]}
#     except HTTPException:
#         raise HTTPException(status_code=401, detail="Invalid or expired token")

# @router.post("/login")
# def login(user_data: schemas.UserLogin, db: Session = Depends(crud.get_db)):
#     return crud.login_user(db, user_data)

# @router.post("/register")
# def register_user(user: schemas.UserCreate, db: Session = Depends(crud.get_db)):
#     return crud.register_user(db, user)

# @router.get("/prices/{source}", response_model=List[schemas.CryptoPrice])
# def get_prices_by_source(source: str, db: Session = Depends(crud.get_db)):
#     return crud.get_prices_by_source(db, source)

# @router.get("/prices/compare/{currency}")
# def compare_prices(currency: str, db: Session = Depends(crud.get_db)):
#     return crud.compare_prices(db, currency)

# @router.get("/prices/max/{currency}")
# def get_max_price(currency: str, db: Session = Depends(crud.get_db)):
#     return crud.get_max_price(db, currency)

# @router.get("/prices/min/{currency}")
# def get_min_price(currency: str, db: Session = Depends(crud.get_db)):
#     return crud.get_min_price(db, currency)

# @router.post("/prices/filter")
# def filter_prices(
#     min_price: float = Body(...),
#     max_price: float = Body(...),
#     source: Optional[str] = Body(None),
#     db: Session = Depends(crud.get_db),
# ):
#     return crud.filter_prices(db, min_price, max_price, source)

# @router.get("/prices/top")
# def get_top_prices(limit: int = 3, db: Session = Depends(crud.get_db)):
#     return crud.get_top_prices(db, limit)
from fastapi import APIRouter, HTTPException, Depends, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.crud import get_db
from app.api import crud
from app.schemas import schemas
from app.service.utils import verify_token
from fastapi.security import OAuth2PasswordBearer
  # Подключаем функцию для получения сессии БД

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.models.models import VBRPrice, InvestingPrice, BitInfoPrice
from sqlalchemy.sql.expression import literal_column
from sqlalchemy.sql import literal


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/convert")
def convert_currency_endpoint(
    request: schemas.ConvertRequest, 
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    user = verify_token(token)
    if not request.source:
        raise HTTPException(status_code=400, detail="Source is required")
    
    result = crud.convert_currency(db, request.from_currency, request.to_currency, request.amount, request.source)
    return result

@router.get("/dashboard")
def get_dashboard(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)
    return {"message": "Welcome to your dashboard!", "user_email": user["sub"]}

@router.post("/login")
def login(user_data: schemas.UserLogin, db: Session = Depends(get_db)):
    return crud.login_user(db, user_data)

@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.register_user(db, user)

@router.get("/prices/{source}", response_model=List[schemas.CryptoPrice])
def get_prices_by_source(source: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return crud.get_prices_by_source(db, source)

@router.get("/prices/compare/{currency}")
def compare_prices(currency: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return crud.compare_prices(db, currency)

@router.get("/prices/max/{currency}")
def get_max_price(currency: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return crud.get_max_price(db, currency)

@router.get("/prices/min/{currency}")
def get_min_price(currency: str, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    verify_token(token)
    return crud.get_min_price(db, currency)



from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional, List



class PriceFilterRequest(BaseModel):
    min_price: float
    max_price: float
    source: Optional[str] = None  # Источник (необязательный параметр)

@router.post("/prices/filter")
def filter_prices(
    request: PriceFilterRequest,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    verify_token(token)

    min_price = request.min_price
    max_price = request.max_price
    source = request.source

    valid_sources = {"VBR", "Investing", "BitInfo"}

    if source and source not in valid_sources:
        raise HTTPException(status_code=400, detail="Invalid source. Valid sources: VBR, Investing, BitInfo")

    queries = []

    if not source or source == "VBR":
        query = db.query(
            VBRPrice.currency, 
            VBRPrice.price, 
            literal("VBR").label("source")  # Исправлено
        ).filter(VBRPrice.price >= min_price, VBRPrice.price <= max_price)
        queries.append(query)

    if not source or source == "Investing":
        query = db.query(
            InvestingPrice.currency, 
            InvestingPrice.price, 
            literal("Investing").label("source")  # Исправлено
        ).filter(InvestingPrice.price >= min_price, InvestingPrice.price <= max_price)
        queries.append(query)

    if not source or source == "BitInfo":
        query = db.query(
            BitInfoPrice.currency, 
            BitInfoPrice.price, 
            literal("BitInfo").label("source")  # Исправлено
        ).filter(BitInfoPrice.price >= min_price, BitInfoPrice.price <= max_price)
        queries.append(query)

    if not queries:
        raise HTTPException(status_code=400, detail="No valid queries generated")

    # Выполняем объединение запросов и получаем результат
    results = queries[0].union(*queries[1:]).all() if len(queries) > 1 else queries[0].all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found in the specified price range")

    return [{"currency": r.currency, "price": r.price, "source": r.source} for r in results]