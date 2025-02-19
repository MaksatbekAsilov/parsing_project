from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import bcrypt
from fastapi import status, HTTPException
import dotenv
import os
dotenv.load_dotenv()  # Загружаем переменные окружения

# Теперь загружаем из .env
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")  # По умолчанию HS256
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

# Эмулируем __about__, если его нет
if not hasattr(bcrypt, "__about__"):
    class About:
        __version__ = bcrypt.__version__
    bcrypt.__about__ = About()

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Функция для хеширования пароля
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Функция для проверки пароля
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Функция для создания JWT-токена
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload  # Возвращаем декодированные данные
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
