from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from . import crud, models, schemas, utils
# uvicorn app.db.main:app --reload
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import dotenv
from fastapi import Query
from .utils import verify_token
from fastapi.security import OAuth2PasswordBearer

dotenv.load_dotenv()
from app.db.database import SessionLocal, engine
# Инициализация базы данных
models.Base.metadata.create_all(bind=engine)

# Создание экземпляра FastAPI
app = FastAPI()

# Разрешаем запросы с любого источника (или можно указать конкретные домены)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Позволяет запросы с любого источника
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все методы (GET, POST и т. д.)
    allow_headers=["*"],  # Разрешает все заголовки
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
@app.get("/dashboard")
def get_dashboard(token: str = Depends(oauth2_scheme)):
    user = verify_token(token)  # Декодируем токен и проверяем его
    return {"message": "Welcome to your dashboard!", "user_email": user["sub"]}


@app.post("/login")
def login(user_data: schemas.UserLogin, db: Session = Depends(crud.get_db)):
    return crud.login_user(db, user_data)


# Эндпоинты для регистрации пользователя
@app.post("/register")
def register_user(user: schemas.UserCreate, db: Session = Depends(crud.get_db)):
    return crud.register_user(db, user)

# Эндпоинты для получения данных
@app.get("/prices/{source}", response_model=List[schemas.CryptoPrice])
def get_prices_by_source(source: str, db: Session = Depends(crud.get_db)):
    return crud.get_prices_by_source(db, source)

@app.get("/prices/compare/{currency}")
def compare_prices(currency: str, db: Session = Depends(crud.get_db)):
    return crud.compare_prices(db, currency)

@app.get("/prices/max/{currency}")
def get_max_price(currency: str, db: Session = Depends(crud.get_db)):
    return crud.get_max_price(db, currency)

@app.get("/prices/min/{currency}")
def get_min_price(currency: str, db: Session = Depends(crud.get_db)):
    return crud.get_min_price(db, currency)

import logging
from fastapi import Query

logging.basicConfig(level=logging.INFO)

from fastapi import HTTPException, Query
from fastapi import Body

@app.post("/prices/filter")
def filter_prices(
    min_price: float = Body(...),
    max_price: float = Body(...),
    source: Optional[str] = Body(None),
    db: Session = Depends(crud.get_db),
):
    return crud.filter_prices(db, min_price, max_price, source)


@app.get("/prices/top")
def get_top_prices(limit: int = 3, db: Session = Depends(crud.get_db)):
    return crud.get_top_prices(db, limit)
