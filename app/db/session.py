from sqlalchemy import Column, String, Float, Integer, create_engine, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker
import dotenv, os

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

# Таблица для сайта VBR
class VBRPrice(Base):
    __tablename__ = "vbr_prices"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

# Таблица для сайта Investing
class InvestingPrice(Base):
    __tablename__ = "investing_prices"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

# Таблица для сайта BitInfo
class BitInfoPrice(Base):
    __tablename__ = "bitinfo_prices"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)

# Создание таблиц в базе данных
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
