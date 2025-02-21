from celery import shared_task
from app.parsing.parsing import CryptoScraper, CryptoDataProcessor
from app.parsing.pars_in_db import DatabaseManager

@shared_task
def update_crypto_prices():
    scraper = CryptoScraper()
    processor = CryptoDataProcessor(scraper)
    db_manager = DatabaseManager()

    try:
        prices = processor.get_crypto_prices()
        print(f"🔥 Полученные цены: {prices}")  # Проверяем, что данные приходят

        if not prices:
            print("⚠️ Данные не получены!")
            return "No data"

        # Предобрабатываем данные и записываем в БД
        prices = db_manager.preprocess_prices(prices)
        db_manager.import_data_to_db(prices)
        
        return prices  # Celery сохранит результат
    except Exception as e:
        print(f"❌ Ошибка в update_crypto_prices: {e}")
        return str(e)
