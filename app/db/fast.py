from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from fastapi import FastAPI, Depends, HTTPException

from pydantic import BaseModel
from typing import List
import dotenv, os
from datetime import datetime

dotenv.load_dotenv()

# Подключение к PostgreSQL
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/crypto"

# Создание базы данных и сессии
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для создания таблиц
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# Модели для таблиц
class VBRPrice(Base):
    __tablename__ = "vbr_prices"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

class InvestingPrice(Base):
    __tablename__ = "investing_prices"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

class BitInfoPrice(Base):
    __tablename__ = "bitinfo_prices"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

# FastAPI приложение
app = FastAPI()

# Модели для ответа
class CryptoPrice(BaseModel):
    currency: str
    price: float
    timestamp: datetime

# Функция для получения сессии
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Эндпоинты для получения данных

@app.get("/prices/vbr", response_model=List[CryptoPrice])
def get_vbr_prices(db: Session = Depends(get_db)):
    prices = db.query(VBRPrice).all()
    return [CryptoPrice(currency=price.currency, price=price.price, timestamp=price.timestamp) for price in prices]

@app.get("/prices/investing", response_model=List[CryptoPrice])
def get_investing_prices(db: Session = Depends(get_db)):
    prices = db.query(InvestingPrice).all()
    return [CryptoPrice(currency=price.currency, price=price.price, timestamp=price.timestamp) for price in prices]

@app.get("/prices/bitinfo", response_model=List[CryptoPrice])
def get_bitinfo_prices(db: Session = Depends(get_db)):
    prices = db.query(BitInfoPrice).all()
    return [CryptoPrice(currency=price.currency, price=price.price, timestamp=price.timestamp) for price in prices]

@app.get("/prices", response_model=List[CryptoPrice])
def get_combined_prices(db: Session = Depends(get_db)):
    vbr_prices = db.query(VBRPrice).all()
    investing_prices = db.query(InvestingPrice).all()
    bitinfo_prices = db.query(BitInfoPrice).all()
    
    combined_prices = []
    combined_prices.extend([CryptoPrice(currency=price.currency, price=price.price, timestamp=price.timestamp) for price in vbr_prices])
    combined_prices.extend([CryptoPrice(currency=price.currency, price=price.price, timestamp=price.timestamp) for price in investing_prices])
    combined_prices.extend([CryptoPrice(currency=price.currency, price=price.price, timestamp=price.timestamp) for price in bitinfo_prices])
    
    return combined_prices

# Запуск приложения
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
