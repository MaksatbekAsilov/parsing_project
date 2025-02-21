from celery import Celery

celery_app = Celery(
    "app",
    broker="redis://127.0.0.1:6379/0",
    backend="redis://127.0.0.1:6379/0"
)

celery_app.autodiscover_tasks(["app.parsing"])  # Автопоиск задач

celery_app.conf.beat_schedule = {
    "update-crypto-prices-every-5-minutes": {
        "task": "app.parsing.tasks.update_crypto_prices",
        "schedule": 120.0,  # здесь меняю время обновления
    },
}

celery_app.conf.timezone = "UTC"
