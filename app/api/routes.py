from fastapi import APIRouter, HTTPException, Depends, Body, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api import crud
from app.schemas import schemas
from app.service.utils import verify_token
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/convert")
def convert_currency_endpoint(request: schemas.ConvertRequest, db: Session = Depends(crud.get_db)):
    if not request.source:
        raise HTTPException(status_code=400, detail="Source is required")
    
    result = crud.convert_currency(db, request.from_currency, request.to_currency, request.amount, request.source)
    return result

@router.get("/dashboard")
def get_dashboard(token: str = Depends(oauth2_scheme)):
    try:
        user = verify_token(token)
        return {"message": "Welcome to your dashboard!", "user_email": user["sub"]}
    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.post("/login")
def login(user_data: schemas.UserLogin, db: Session = Depends(crud.get_db)):
    return crud.login_user(db, user_data)

@router.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(crud.get_db)):
    return crud.register_user(db, user)

@router.get("/prices/{source}", response_model=List[schemas.CryptoPrice])
def get_prices_by_source(source: str, db: Session = Depends(crud.get_db)):
    return crud.get_prices_by_source(db, source)

@router.get("/prices/compare/{currency}")
def compare_prices(currency: str, db: Session = Depends(crud.get_db)):
    return crud.compare_prices(db, currency)

@router.get("/prices/max/{currency}")
def get_max_price(currency: str, db: Session = Depends(crud.get_db)):
    return crud.get_max_price(db, currency)

@router.get("/prices/min/{currency}")
def get_min_price(currency: str, db: Session = Depends(crud.get_db)):
    return crud.get_min_price(db, currency)

@router.post("/prices/filter")
def filter_prices(
    min_price: float = Body(...),
    max_price: float = Body(...),
    source: Optional[str] = Body(None),
    db: Session = Depends(crud.get_db),
):
    return crud.filter_prices(db, min_price, max_price, source)

@router.get("/prices/top")
def get_top_prices(limit: int = 3, db: Session = Depends(crud.get_db)):
    return crud.get_top_prices(db, limit)
