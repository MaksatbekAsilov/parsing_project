from sqlalchemy.orm import Session
from contextlib import contextmanager
from datetime import datetime
from app.db.session import SessionLocal, VBRPrice, InvestingPrice, BitInfoPrice
# python -m app.parsing.pars_in_db


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

    def preprocess_prices(self, data: list) -> list:
        """
        Преобразует строковые цены в числа и удаляет лишние пробелы.
        """
        for item in data:
            item["vbr_price"] = float(item["vbr_price"].replace(" ", ""))
            item["investing_price"] = float(item["investing_price"].replace(" ", ""))
            item["bitinfo_price"] = float(item["bitinfo_price"].replace(" ", ""))
        return data

    def import_data_to_db(self, data: list):
        """
        Импортирует данные в соответствующие таблицы в базе данных.
        Обновляет записи, если они существуют для валюты.
        """
        with self.get_db_session() as db:
            for item in data:
                # Запись для VBR
                vbr_record = db.query(VBRPrice).filter(VBRPrice.currency == item["currency"]).first()
                if vbr_record:
                    vbr_record.price = item["vbr_price"]
                    vbr_record.timestamp = datetime.utcnow()  # Обновляем временную метку
                else:
                    vbr_price = VBRPrice(
                        currency=item["currency"],
                        price=item["vbr_price"],
                        timestamp=datetime.utcnow()
                    )
                    db.add(vbr_price)

                # Запись для Investing
                investing_record = db.query(InvestingPrice).filter(InvestingPrice.currency == item["currency"]).first()
                if investing_record:
                    investing_record.price = item["investing_price"]
                    investing_record.timestamp = datetime.utcnow()  # Обновляем временную метку
                else:
                    investing_price = InvestingPrice(
                        currency=item["currency"],
                        price=item["investing_price"],
                        timestamp=datetime.utcnow()
                    )
                    db.add(investing_price)

                # Запись для BitInfo
                bitinfo_record = db.query(BitInfoPrice).filter(BitInfoPrice.currency == item["currency"]).first()
                if bitinfo_record:
                    bitinfo_record.price = item["bitinfo_price"]
                    bitinfo_record.timestamp = datetime.utcnow()  # Обновляем временную метку
                else:
                    bitinfo_price = BitInfoPrice(
                        currency=item["currency"],
                        price=item["bitinfo_price"],
                        timestamp=datetime.utcnow()
                    )
                    db.add(bitinfo_price)

            db.commit()  # Сохраняем изменения


if __name__ == "__main__":
    from app.parsing.parsing import CryptoScraper, CryptoDataProcessor

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
