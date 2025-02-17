# from fastapi import FastAPI, HTTPException, Depends
# from sqlalchemy.orm import Session
# from . import crud
# from ..schemas import schemas
# from ..service import utils
# from ..models import models
# # uvicorn app.api.main:app --reload
# from fastapi.middleware.cors import CORSMiddleware
# from typing import List, Optional
# import dotenv
# from fastapi import Query
# from ..service.utils import verify_token
# from fastapi.security import OAuth2PasswordBearer
# from .crud import get_db, compare_prices, convert_currency
# from ..schemas.schemas import ConvertRequest
# from fastapi import HTTPException, Query
# from fastapi import Body
# import logging
# from fastapi import Query


# dotenv.load_dotenv()
# from app.models.database import SessionLocal, engine
# # Инициализация базы данных
# models.Base.metadata.create_all(bind=engine)
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
# # Создание экземпляра FastAPI
# app = FastAPI()

# # Разрешаем запросы с любого источника (или можно указать конкретные домены)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Позволяет запросы с любого источника
#     allow_credentials=True,
#     allow_methods=["*"],  # Разрешает все методы (GET, POST и т. д.)
#     allow_headers=["*"],  # Разрешает все заголовки
# )

# @app.post("/convert")
# def convert_currency_endpoint(request: ConvertRequest, db: Session = Depends(crud.get_db)):
#     if not request.source:  # Проверка на пустой выбор источника
#         raise HTTPException(status_code=400, detail="Source is required")
    
#     result = convert_currency(db, request.from_currency, request.to_currency, request.amount, request.source)
#     return result

# @app.get("/dashboard")
# def get_dashboard(token: str = Depends(oauth2_scheme)):
#     try:
#         user = verify_token(token)  # Декодируем токен и проверяем его
#         return {"message": "Welcome to your dashboard!", "user_email": user["sub"]}
#     except HTTPException as e:
#         raise HTTPException(status_code=401, detail="Неверный или просроченный токен")


# @app.post("/login")
# def login(user_data: schemas.UserLogin, db: Session = Depends(crud.get_db)):
#     return crud.login_user(db, user_data)

# # Эндпоинты для регистрации пользователя
# @app.post("/register")
# def register_user(user: schemas.UserCreate, db: Session = Depends(crud.get_db)):
#     return crud.register_user(db, user)

# # Эндпоинты для получения данных
# @app.get("/prices/{source}", response_model=List[schemas.CryptoPrice])
# def get_prices_by_source(source: str, db: Session = Depends(crud.get_db)):
#     return crud.get_prices_by_source(db, source)

# @app.get("/prices/compare/{currency}")
# def compare_prices(currency: str, db: Session = Depends(crud.get_db)):
#     return crud.compare_prices(db, currency)

# @app.get("/prices/max/{currency}")
# def get_max_price(currency: str, db: Session = Depends(crud.get_db)):
#     return crud.get_max_price(db, currency)

# @app.get("/prices/min/{currency}")
# def get_min_price(currency: str, db: Session = Depends(crud.get_db)):
#     return crud.get_min_price(db, currency)

# logging.basicConfig(level=logging.INFO)

# @app.post("/prices/filter")
# def filter_prices(
#     min_price: float = Body(...),
#     max_price: float = Body(...),
#     source: Optional[str] = Body(None),
#     db: Session = Depends(crud.get_db),
# ):
#     return crud.filter_prices(db, min_price, max_price, source)

# @app.get("/prices/top")
# def get_top_prices(limit: int = 3, db: Session = Depends(crud.get_db)):
#     return crud.get_top_prices(db, limit)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import models
from app.models.database import engine
from app.api.routes import router  # Импортируем маршруты из api/routes.py
# uvicorn app.main:app --reload

# Инициализация базы данных
models.Base.metadata.create_all(bind=engine)

# Создание экземпляра FastAPI
app = FastAPI()

# Разрешаем запросы с любого источника
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты
app.include_router(router)

# Тестовый эндпоинт
@app.get("/")
def root():
    return {"message": "API is running 🚀"}
