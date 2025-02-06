from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import create_engine, func, and_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
from pydantic import BaseModel
from typing import List, Optional
import dotenv, os
from datetime import datetime
from sqlalchemy import literal_column
from passlib.context import CryptContext  # Для хеширования пароля

dotenv.load_dotenv()

# Подключение к PostgreSQL
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/crypto"

# Создание базы данных и сессии
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Настройка для хеширования пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Модели таблиц
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

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Разрешаем запросы с любого источника (или можно указать конкретные домены)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Позволяет запросы с любого источника
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все методы (GET, POST и т. д.)
    allow_headers=["*"],  # Разрешает все заголовки
)



# Модели для ответа
class CryptoPrice(BaseModel):
    currency: str
    price: float
    timestamp: datetime

class PriceStats(BaseModel):
    min_price: float
    max_price: float

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
    return db.query(VBRPrice).all()

@app.get("/prices/investing", response_model=List[CryptoPrice])
def get_investing_prices(db: Session = Depends(get_db)):
    return db.query(InvestingPrice).all()

@app.get("/prices/bitinfo", response_model=List[CryptoPrice])
def get_bitinfo_prices(db: Session = Depends(get_db)):
    return db.query(BitInfoPrice).all()

@app.get("/prices", response_model=List[CryptoPrice])
def get_combined_prices(db: Session = Depends(get_db)):
    return db.query(VBRPrice).all() + db.query(InvestingPrice).all() + db.query(BitInfoPrice).all()

# Эндпоинт цены по криптовалюте с 3 сайтов
@app.get("/prices/compare/{currency}")
def compare_prices(currency: str, db: Session = Depends(get_db)):
    vbr = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.timestamp.desc()).first()
    investing = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.timestamp.desc()).first()
    bitinfo = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.timestamp.desc()).first()
    
    if not (vbr or investing or bitinfo):
        raise HTTPException(status_code=404, detail="Currency not found in any source")
    
    return {
        "currency": currency,
        "prices": {
            "vbr": vbr.price if vbr else None,
            "investing": investing.price if investing else None,
            "bitinfo": bitinfo.price if bitinfo else None
        }
    }

## Максимум и минимум
@app.get("/prices/max/{currency}")
def get_max_price(currency: str, db: Session = Depends(get_db)):
    # Get the maximum price across all sources
    vbr_max = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.price.desc()).first()
    investing_max = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.price.desc()).first()
    bitinfo_max = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.price.desc()).first()

    max_price = None
    source = None

    # Determine the highest price and source
    if vbr_max and (max_price is None or vbr_max.price > max_price):
        max_price = vbr_max.price
        source = "VBR"
    if investing_max and (max_price is None or investing_max.price > max_price):
        max_price = investing_max.price
        source = "Investing"
    if bitinfo_max and (max_price is None or bitinfo_max.price > max_price):
        max_price = bitinfo_max.price
        source = "BitInfo"

    if max_price is None:
        raise HTTPException(status_code=404, detail="Currency not found in any source")

    return {
        "currency": currency,
        "max_price": max_price,
        "source": source
    }

@app.get("/prices/min/{currency}")
def get_min_price(currency: str, db: Session = Depends(get_db)):
    # Get the minimum price across all sources
    vbr_min = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.price.asc()).first()
    investing_min = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.price.asc()).first()
    bitinfo_min = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.price.asc()).first()

    min_price = None
    source = None

    # Determine the lowest price and source
    if vbr_min and (min_price is None or vbr_min.price < min_price):
        min_price = vbr_min.price
        source = "VBR"
    if investing_min and (min_price is None or investing_min.price < min_price):
        min_price = investing_min.price
        source = "Investing"
    if bitinfo_min and (min_price is None or bitinfo_min.price < min_price):
        min_price = bitinfo_min.price
        source = "BitInfo"

    if min_price is None:
        raise HTTPException(status_code=404, detail="Currency not found in any source")

    return {
        "currency": currency,
        "min_price": min_price,
        "source": source
    }

@app.get("/prices/filter")
def filter_prices(min_price: float = None, max_price: float = None, db: Session = Depends(get_db)):
    # Создаем запросы для каждой таблицы с добавлением названия сайта
    vbr_query = db.query(
        VBRPrice.currency, 
        VBRPrice.price, 
        literal_column("'VBR'").label("source")
    ).filter(
        (min_price is None or VBRPrice.price >= min_price) & 
        (max_price is None or VBRPrice.price <= max_price)
    )

    investing_query = db.query(
        InvestingPrice.currency, 
        InvestingPrice.price, 
        literal_column("'Investing'").label("source")
    ).filter(
        (min_price is None or InvestingPrice.price >= min_price) & 
        (max_price is None or InvestingPrice.price <= max_price)
    )

    bitinfo_query = db.query(
        BitInfoPrice.currency, 
        BitInfoPrice.price, 
        literal_column("'BitInfo'").label("source")
    ).filter(
        (min_price is None or BitInfoPrice.price >= min_price) & 
        (max_price is None or BitInfoPrice.price <= max_price)
    )

    # Объединяем результаты всех запросов
    results = vbr_query.union(investing_query).union(bitinfo_query).all()

    if not results:
        raise HTTPException(status_code=404, detail="No currencies found in this price range")

    # Возвращаем результат с добавлением названия источника
    return [{"currency": result.currency, "price": result.price, "source": result.source} for result in results]


@app.get("/prices/top")
def get_top_prices(limit: int = 3, db: Session = Depends(get_db)):
    vbr_top = db.query(VBRPrice).order_by(VBRPrice.price.desc()).limit(limit).all()
    investing_top = db.query(InvestingPrice).order_by(InvestingPrice.price.desc()).limit(limit).all()
    bitinfo_top = db.query(BitInfoPrice).order_by(BitInfoPrice.price.desc()).limit(limit).all()

    top_prices = []

    for source, prices in [("VBR", vbr_top), ("Investing", investing_top), ("BitInfo", bitinfo_top)]:
        for price in prices:
            top_prices.append({
                "currency": price.currency,
                "price": price.price,
                "source": source
            })

    # Limiting results to the specified limit
    return top_prices[:limit]


# Регистрация пользователя
@app.post("/register")  # Должно быть именно @app.post!
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
