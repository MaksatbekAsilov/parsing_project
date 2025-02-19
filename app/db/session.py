from sqlalchemy import Column, String, Float, Integer, create_engine, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
import dotenv, os
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

# Модель для пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# Модели для таблиц цен с разных сайтов
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

# Хеширование пароля
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


