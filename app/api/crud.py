# from sqlalchemy.orm import Session
# from fastapi import HTTPException
# from ..models.models import User, VBRPrice, InvestingPrice, BitInfoPrice
# from ..schemas.schemas import UserCreate, CryptoPrice
# from ..models.database import SessionLocal, engine
# from sqlalchemy import literal_column
# from ..service.utils import hash_password
# from fastapi import Query
# import logging
# from ..schemas.schemas import UserLogin
# from ..service.utils import verify_password, create_access_token
# from jose import JWTError, jwt
# from ..service.utils import SECRET_KEY, ALGORITHM
# from fastapi import status
# from fastapi import HTTPException, Query
# import logging
# from typing import Optional

# # Функция фильтрации цен
# from fastapi import Depends


# # Функция для получения сессии с БД
# def get_db():
#     db = SessionLocal()  # Подключение через SessionLocal
#     try:
#         yield db
#     finally:
#         db.close()

# def login_user(db: Session, user_data: UserLogin):
#     # Ищем пользователя по email
#     user = db.query(User).filter(User.email == user_data.email).first()

#     # Если пользователь не найден или пароль не совпадает
#     if not user or not verify_password(user_data.password, user.hashed_password):
#         # Возвращаем общую ошибку без указания подробностей
#         raise HTTPException(status_code=401, detail="Неверные учетные данные")

#     # Генерация JWT токена
#     access_token = create_access_token(data={"sub": user.email})

#     return {"token": access_token}

# # Функция для регистрации пользователя
# def register_user(db: Session, user: UserCreate):
#     # Проверка на существование email
#     existing_email = db.query(User).filter(User.email == user.email).first()
#     if existing_email:
#         raise HTTPException(status_code=400, detail="Этот email занят, сорян")

#     # Хеширование пароля и создание нового пользователя
#     hashed_password = hash_password(user.password)
#     new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)

#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)

#     return {"message": "Регистрация прошла успешно, поздравляю"}

# # Функция для получения цен по источникам
# def get_prices_by_source(db: Session, source: str):
#     if source == "vbr":
#         return db.query(VBRPrice).all()
#     elif source == "investing":
#         return db.query(InvestingPrice).all()
#     elif source == "bitinfo":
#         return db.query(BitInfoPrice).all()
#     else:
#         raise HTTPException(status_code=400, detail="Invalid source")

# # Функция для сравнения цен по валютам
# def compare_prices1(db: Session, from_currency: str, to_currency: str):
#     vbr_from = db.query(VBRPrice).filter(VBRPrice.currency.ilike(from_currency)).order_by(VBRPrice.timestamp.desc()).first()
#     investing_from = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(from_currency)).order_by(InvestingPrice.timestamp.desc()).first()
#     bitinfo_from = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(from_currency)).order_by(BitInfoPrice.timestamp.desc()).first()

#     vbr_to = db.query(VBRPrice).filter(VBRPrice.currency.ilike(to_currency)).order_by(VBRPrice.timestamp.desc()).first()
#     investing_to = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(to_currency)).order_by(InvestingPrice.timestamp.desc()).first()
#     bitinfo_to = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(to_currency)).order_by(BitInfoPrice.timestamp.desc()).first()

#     if not (vbr_from or investing_from or bitinfo_from) or not (vbr_to or investing_to or bitinfo_to):
#         raise HTTPException(status_code=404, detail="Currency not found in any source")

#     # Пример использования VBR данных
#     from_price = vbr_from.price if vbr_from else investing_from.price if investing_from else bitinfo_from.price
#     to_price = vbr_to.price if vbr_to else investing_to.price if investing_to else bitinfo_to.price

#     return {
#         "from_currency": from_currency,
#         "to_currency": to_currency,
#         "rate": from_price / to_price,
#         "converted_price": (from_price / to_price) * 1.0  # Пример с amount = 1
#     }

# def compare_prices(db: Session, currency: str):
#     vbr = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.timestamp.desc()).first()
#     investing = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.timestamp.desc()).first()
#     bitinfo = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.timestamp.desc()).first()

#     if not (vbr or investing or bitinfo):
#         raise HTTPException(status_code=404, detail="Currency not found in any source")
    
#     return {
#         "currency": currency,
#         "prices": {
#             "vbr": vbr.price if vbr else None,
#             "investing": investing.price if investing else None,
#             "bitinfo": bitinfo.price if bitinfo else None
#         }
#     }

# def convert_currency(db: Session, from_currency: str, to_currency: str, amount: float, source: str):
#     if not source:
#         raise HTTPException(status_code=400, detail="Source is required")

#     prices = compare_prices1(db, from_currency, to_currency)

#     # Получаем курс обмена
#     rate = prices["rate"]

#     # Конвертируем валюту и округляем до 2 знаков после запятой
#     converted_price = round(rate * amount, 2)

#     return {
#         "from_currency": from_currency,
#         "to_currency": to_currency,
#         "rate": round(rate, 2),  # Округляем и курс до 2 знаков
#         "converted_price": converted_price
#     }

# # Функция для получения максимальной цены по валюте
# def get_max_price(db: Session, currency: str):
#     vbr_max = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.price.desc()).first()
#     investing_max = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.price.desc()).first()
#     bitinfo_max = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.price.desc()).first()

#     max_price = None
#     source = None

#     if vbr_max and (max_price is None or vbr_max.price > max_price):
#         max_price = vbr_max.price
#         source = "VBR"
#     if investing_max and (max_price is None or investing_max.price > max_price):
#         max_price = investing_max.price
#         source = "Investing"
#     if bitinfo_max and (max_price is None or bitinfo_max.price > max_price):
#         max_price = bitinfo_max.price
#         source = "BitInfo"

#     if max_price is None:
#         raise HTTPException(status_code=404, detail="Currency not found in any source")

#     return {
#         "currency": currency,
#         "max_price": max_price,
#         "source": source
#     }

# # Функция для получения минимальной цены по валюте
# def get_min_price(db: Session, currency: str):
#     vbr_min = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.price.asc()).first()
#     investing_min = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.price.asc()).first()
#     bitinfo_min = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.price.asc()).first()

#     min_price = None
#     source = None

#     if vbr_min and (min_price is None or vbr_min.price < min_price):
#         min_price = vbr_min.price
#         source = "VBR"
#     if investing_min and (min_price is None or investing_min.price < min_price):
#         min_price = investing_min.price
#         source = "Investing"
#     if bitinfo_min and (min_price is None or bitinfo_min.price < min_price):
#         min_price = bitinfo_min.price
#         source = "BitInfo"

#     if min_price is None:
#         raise HTTPException(status_code=404, detail="Currency not found in any source")

#     return {
#         "currency": currency,
#         "min_price": min_price,
#         "source": source
#     }

# def filter_prices(db: Session, min_price: float, max_price: float, source: Optional[str] = None):
#     if min_price is None or max_price is None:
#         raise HTTPException(status_code=400, detail="Both min_price and max_price are required.")
    
#     # Преобразование min_price и max_price в числа
#     try:
#         min_price = float(min_price)
#         max_price = float(max_price)
#     except ValueError:
#         raise HTTPException(status_code=400, detail="min_price and max_price must be valid numbers")

#     # Фильтрация по источникам
#     queries = []

#     # Список допустимых источников
#     valid_sources = {"VBR", "Investing", "BitInfo"}

#     # Если source передан, проверяем его на валидность
#     if source and source not in valid_sources:
#         raise HTTPException(status_code=400, detail="Invalid source. Valid sources: VBR, Investing, BitInfo")
    
#     # Построение запросов для каждого источника
#     if not source or source == "VBR":
#         query = db.query(VBRPrice.currency, VBRPrice.price, literal_column("'VBR'").label("source"))
#         query = query.filter(VBRPrice.price >= min_price, VBRPrice.price <= max_price)
#         queries.append(query)

#     if not source or source == "Investing":
#         query = db.query(InvestingPrice.currency, InvestingPrice.price, literal_column("'Investing'").label("source"))
#         query = query.filter(InvestingPrice.price >= min_price, InvestingPrice.price <= max_price)
#         queries.append(query)

#     if not source or source == "BitInfo":
#         query = db.query(BitInfoPrice.currency, BitInfoPrice.price, literal_column("'BitInfo'").label("source"))
#         query = query.filter(BitInfoPrice.price >= min_price, BitInfoPrice.price <= max_price)
#         queries.append(query)

#     if not queries:
#         raise HTTPException(status_code=400, detail="No valid queries generated")

#     # Объединение результатов
#     results = queries[0].union(*queries[1:]).all() if len(queries) > 1 else queries[0].all()

#     if not results:
#         raise HTTPException(status_code=404, detail="No results found in the specified price range")
    
#     return [{"currency": r.currency, "price": r.price, "source": r.source} for r in results]

# # Функция для получения топ-цен
# def get_top_prices(db: Session, limit: int):
#     vbr_top = db.query(VBRPrice).order_by(VBRPrice.price.desc()).limit(limit).all()
#     investing_top = db.query(InvestingPrice).order_by(InvestingPrice.price.desc()).limit(limit).all()
#     bitinfo_top = db.query(BitInfoPrice).order_by(BitInfoPrice.price.desc()).limit(limit).all()

#     top_prices = []

#     for source, prices in [("VBR", vbr_top), ("Investing", investing_top), ("BitInfo", bitinfo_top)]:
#         for price in prices:
#             top_prices.append({
#                 "currency": price.currency,
#                 "price": price.price,
#                 "source": source
#             })

#     return top_prices[:limit]

from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends, status
from ..models.models import User, VBRPrice, InvestingPrice, BitInfoPrice
from ..schemas.schemas import UserCreate, CryptoPrice, UserLogin
from ..models.database import SessionLocal
from ..service.utils import hash_password, verify_password, create_access_token
from jose import JWTError, jwt
from ..service.utils import SECRET_KEY, ALGORITHM
from fastapi.security import OAuth2PasswordBearer
from typing import Optional
from sqlalchemy import literal_column

# Аутентификация
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

def login_user(db: Session, user_data: UserLogin):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": user.email})
    return {"token": access_token}

def register_user(db: Session, user: UserCreate):
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Емейл занят, сорян")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Зарегался, можешь входить"}

def get_prices_by_source(db: Session, source: str, current_user: User = Depends(get_current_user)):
    if source == "vbr":
        return db.query(VBRPrice).all()
    elif source == "investing":
        return db.query(InvestingPrice).all()
    elif source == "bitinfo":
        return db.query(BitInfoPrice).all()
    else:
        raise HTTPException(status_code=400, detail="Invalid source")

def compare_prices(db: Session, currency: str, current_user: User = Depends(get_current_user)):
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

def convert_currency(db: Session, from_currency: str, to_currency: str, amount: float, source: str, current_user: User = Depends(get_current_user)):
    # Получаем цены обеих валют
    prices_from = compare_prices(db, from_currency)
    prices_to = compare_prices(db, to_currency)

    rate_from = prices_from["prices"].get(source.lower())
    rate_to = prices_to["prices"].get(source.lower())

    if rate_from is None or rate_to is None:
        raise HTTPException(status_code=404, detail=f"No data for source {source}")

    # Формула конверсии
    converted_price = round((amount * rate_from) / rate_to, 8)  # Дробные значения для точности

    return {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "rate": round(rate_from / rate_to, 8),  # Сам курс обмена
        "converted_price": converted_price
    }


def get_max_price(db: Session, currency: str, current_user: User = Depends(get_current_user)):
    vbr_max = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.price.desc()).first()
    investing_max = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.price.desc()).first()
    bitinfo_max = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.price.desc()).first()
    max_price = max([p.price for p in [vbr_max, investing_max, bitinfo_max] if p], default=None)
    if max_price is None:
        raise HTTPException(status_code=404, detail="Currency not found in any source")
    return {"currency": currency, "max_price": max_price}

def get_min_price(db: Session, currency: str, current_user: User = Depends(get_current_user)):
    vbr_min = db.query(VBRPrice).filter(VBRPrice.currency.ilike(currency)).order_by(VBRPrice.price.asc()).first()
    investing_min = db.query(InvestingPrice).filter(InvestingPrice.currency.ilike(currency)).order_by(InvestingPrice.price.asc()).first()
    bitinfo_min = db.query(BitInfoPrice).filter(BitInfoPrice.currency.ilike(currency)).order_by(BitInfoPrice.price.asc()).first()
    min_price = min([p.price for p in [vbr_min, investing_min, bitinfo_min] if p], default=None)
    if min_price is None:
        raise HTTPException(status_code=404, detail="Currency not found in any source")
    return {"currency": currency, "min_price": min_price}

def filter_prices(db: Session, min_price: float, max_price: float, source: Optional[str] = None):
    if min_price is None or max_price is None:
        raise HTTPException(status_code=400, detail="Both min_price and max_price are required.")

    try:
        min_price = float(min_price)
        max_price = float(max_price)
    except ValueError:
        raise HTTPException(status_code=400, detail="min_price and max_price must be valid numbers")

    queries = []
    valid_sources = {"VBR", "Investing", "BitInfo"}

    if source and source not in valid_sources:
        raise HTTPException(status_code=400, detail="Invalid source. Valid sources: VBR, Investing, BitInfo")

    if not source or source == "VBR":
        query = db.query(VBRPrice.currency, VBRPrice.price, literal_column("'VBR'").label("source"))
        query = query.filter(VBRPrice.price >= min_price, VBRPrice.price <= max_price)
        queries.append(query)

    if not source or source == "Investing":
        query = db.query(InvestingPrice.currency, InvestingPrice.price, literal_column("'Investing'").label("source"))
        query = query.filter(InvestingPrice.price >= min_price, InvestingPrice.price <= max_price)
        queries.append(query)

    if not source or source == "BitInfo":
        query = db.query(BitInfoPrice.currency, BitInfoPrice.price, literal_column("'BitInfo'").label("source"))
        query = query.filter(BitInfoPrice.price >= min_price, BitInfoPrice.price <= max_price)
        queries.append(query)

    if not queries:
        raise HTTPException(status_code=400, detail="No valid queries generated")

    results = queries[0].union(*queries[1:]).all() if len(queries) > 1 else queries[0].all()

    if not results:
        raise HTTPException(status_code=404, detail="No results found in the specified price range")
    
    return [{"currency": r.currency, "price": r.price, "source": r.source} for r in results]