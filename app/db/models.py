from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()

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

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
