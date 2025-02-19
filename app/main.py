# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from app.models import models
# from app.models.database import engine
# from app.api.routes import router  # Импортируем маршруты из api/routes.py
# # uvicorn app.main:app --reload

# # Инициализация базы данных
# models.Base.metadata.create_all(bind=engine)

# # Создание экземпляра FastAPI
# app = FastAPI()

# # Разрешаем запросы с любого источника
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Подключаем маршруты
# app.include_router(router)

# # Тестовый эндпоинт
# @app.get("/")
# def root():
#     return {"message": "API is running 🚀"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.models import models
from app.models.database import engine
from app.api.routes import router  # uvicorn app.main:app --reload
import subprocess
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Функция для запуска миграций
def run_migrations():
    try:
        logger.info("Запуск миграций Alembic...")
        subprocess.run(["alembic", "upgrade", "head"], check=True)
        logger.info("Миграции успешно применены.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Ошибка при выполнении миграций: {e}")
        raise

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

# Запуск миграций только при старте через `uvicorn main:app`
if __name__ == "__main__":
    run_migrations()
