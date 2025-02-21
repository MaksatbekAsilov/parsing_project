from app.parsing.parsing import CryptoScraper

scraper = CryptoScraper()
data = scraper.scrape()
print(f"Полученные данные: {data}")

# celery -A app.celery_app worker --loglevel=info --pool=solo
# celery -A app.celery_app beat --loglevel=info
