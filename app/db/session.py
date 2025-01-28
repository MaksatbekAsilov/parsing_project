from sqlalchemy import Column, String, Float, Integer, create_engine, DateTime, func
from sqlalchemy.orm import declarative_base, sessionmaker

# Подключение к PostgreSQL
DATABASE_URL = "postgresql://postgres:12345@localhost:5432/crypto"

# Создание базы данных и сессии
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс моделей
Base = declarative_base()

# SQLAlchemy модель
class CryptoPriceModel(Base):
    __tablename__ = "crypto_prices_with_date"
    id = Column(Integer, primary_key=True, index=True)
    currency = Column(String, index=True, nullable=False)
    vbr_price = Column(Float, nullable=False)
    investing_price = Column(Float, nullable=False)
    bitinfo_price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=func.now(), nullable=False)  # Поле для времени записи

# Создание таблиц в базе данных
if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
