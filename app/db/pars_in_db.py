from sqlalchemy.orm import Session
from typing import List
from contextlib import contextmanager
from datetime import datetime
from app.db.session import SessionLocal, CryptoPriceModel 


class DatabaseManager:
    """
    Класс для управления базой данных, включая подключение, обработку и сохранение данных.
    """
    def __init__(self):
        self.session_factory = SessionLocal

    @contextmanager
    def get_db_session(self):
        """
        Контекстный менеджер для работы с сессией базы данных.
        """
        db = self.session_factory()
        try:
            yield db
        finally:
            db.close()

    def preprocess_prices(self, data: List[dict]) -> List[dict]:
        """
        Преобразует строковые цены в числа и удаляет лишние пробелы.
        """
        for item in data:
            item["vbr_price"] = float(item["vbr_price"].replace(" ", ""))
            item["investing_price"] = float(item["investing_price"].replace(" ", ""))
            item["bitinfo_price"] = float(item["bitinfo_price"].replace(" ", ""))
        return data

    def import_data_to_db(self, data: List[dict]):
        """
        Импортирует данные в базу данных, обновляя существующие записи по валюте и времени.
        """
        with self.get_db_session() as db:
            for item in data:
                # Проверка, существует ли запись с таким же валютным курсом и временной меткой
                existing_record = db.query(CryptoPriceModel).filter_by(
                    currency=item["currency"], 
                    timestamp=datetime.utcnow().date()  # используем только дату для проверки
                ).first()

                if existing_record:
                    # Если запись существует, обновляем её
                    existing_record.vbr_price = item["vbr_price"]
                    existing_record.investing_price = item["investing_price"]
                    existing_record.bitinfo_price = item["bitinfo_price"]
                    existing_record.timestamp = datetime.utcnow()  # Обновляем временную метку
                else:
                    # Если записи нет, создаём новую
                    db_crypto = CryptoPriceModel(
                        currency=item["currency"],
                        vbr_price=item["vbr_price"],
                        investing_price=item["investing_price"],
                        bitinfo_price=item["bitinfo_price"],
                        timestamp=datetime.utcnow()  # Текущий момент времени
                    )
                    db.add(db_crypto)
            db.commit()  # Сохраняем изменения в базе данных


if __name__ == "__main__":
    from app.parsing import CryptoScraper, CryptoDataProcessor

    # Создаём экземпляры классов
    scraper = CryptoScraper()
    processor = CryptoDataProcessor(scraper)
    db_manager = DatabaseManager()

    # Получаем данные из парсинга
    crypto_prices = processor.get_crypto_prices()

    # Предобрабатываем данные
    crypto_prices = db_manager.preprocess_prices(crypto_prices)

    # Импортируем данные в базу
    db_manager.import_data_to_db(crypto_prices)
