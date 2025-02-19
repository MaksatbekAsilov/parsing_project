import os
from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем данные из .env
POSTGRES_HOST = os.getenv('POSTGRES_HOST')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')

SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:5432/crypto"

# Настройка логирования Alembic
config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Устанавливаем URL для Alembic
config.set_main_option("sqlalchemy.url", SQLALCHEMY_DATABASE_URL)

# Импортируем метаданные моделей
from app.models.models import Base  # Убедись, что путь правильный

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Запуск миграций в 'offline' режиме."""
    context.configure(
        url=SQLALCHEMY_DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Запуск миграций в 'online' режиме."""
    engine = create_engine(SQLALCHEMY_DATABASE_URL, poolclass=pool.NullPool)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
