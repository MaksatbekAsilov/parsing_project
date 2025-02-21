# import requests
# from bs4 import BeautifulSoup
# import re

# class CryptoScraper:
#     def __init__(self):
#         self.vbr_url = "https://www.vbr.ru/crypto/"
#         self.investing_url = "https://ru.investing.com/crypto"
#         self.bitinfo_url = "https://bitinfocharts.com/ru/crypto-kurs/"

#     @staticmethod
#     def clean_price(price: str):
#         # Убираем все точки, кроме одной между целой и дробной частью
#         price = re.sub(r'\.(?=.*\.)', '', price)
#         return price

#     def get_vbr_data(self):
#         response = requests.get(self.vbr_url)
#         soup = BeautifulSoup(response.text, "html.parser")

#         coins = soup.select('table tbody tr')
#         vbr_data = {}

#         for coin in coins:
#             name_tag = coin.select_one('td:nth-child(1) span')
#             price_tag = coin.select_one('td:nth-child(3) div')

#             if name_tag and price_tag:
#                 name = name_tag.text
#                 price = price_tag.text.replace(' $', '')  # Убираем знак доллара
#                 vbr_data[name] = price

#         return vbr_data

#     def get_investing_data(self):
#         response = requests.get(self.investing_url)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         table_rows = soup.select('div:nth-of-type(5) > div > div:nth-of-type(2) > div:nth-of-type(1) > table > tbody > tr')

#         investing_data = {}
#         for i in range(25):
#             try:
#                 currency_name = table_rows[i].select_one('td:nth-of-type(3)').get_text(strip=True)
#                 numeric_value = table_rows[i].select_one('td:nth-of-type(4) > span').get_text(strip=True)
#                 investing_data[currency_name] = numeric_value
#             except Exception:
#                 pass

#         return investing_data

#     def get_bitinfo_data(self):
#         response = requests.get(self.bitinfo_url)
#         soup = BeautifulSoup(response.text, 'html.parser')
#         rows = soup.select('table tbody tr')

#         bitinfo_data = {}
#         for i in range(25):
#             try:
#                 currency_name = rows[i].select_one('td:nth-of-type(1)').text.strip()
#                 short_name = currency_name.split()[0]
#                 price = rows[i].select_one('td:nth-of-type(2) a').text.strip()
#                 price = re.sub(r'[^\d.]', '', price)  # Убираем все нецифровые символы, кроме точки
#                 bitinfo_data[short_name] = price
#             except Exception:
#                 pass

#         return bitinfo_data

# class CryptoDataProcessor:
#     def __init__(self, scraper):
#         self.scraper = scraper

#     def get_crypto_prices(self):
#         vbr_data = self.scraper.get_vbr_data()
#         investing_data = self.scraper.get_investing_data()
#         bitinfo_data = self.scraper.get_bitinfo_data()

#         common_currencies = set(vbr_data.keys()) & set(investing_data.keys()) & set(bitinfo_data.keys())

#         # Желаемый порядок валют
#         desired_order = ["SOL", "BTC", "LINK", "DOGE", "ADA", "BNB", "LTC", "ETH", "XRP"]

#         crypto_prices = []

#         for currency in desired_order:
#             if currency in common_currencies:
#                 vbr_price = self.scraper.clean_price(vbr_data[currency].replace(',', '.'))
#                 investing_price = self.scraper.clean_price(investing_data[currency].replace(',', '.'))
#                 bitinfo_price = self.scraper.clean_price(bitinfo_data[currency].replace(',', '.'))

#                 crypto_prices.append({
#                     "currency": currency,
#                     "vbr_price": vbr_price,
#                     "investing_price": investing_price,
#                     "bitinfo_price": bitinfo_price
#                 })

#         return crypto_prices

# if __name__ == "__main__":
#     scraper = CryptoScraper()
#     processor = CryptoDataProcessor(scraper)

#     prices = processor.get_crypto_prices()
#     print(prices)


import requests
from bs4 import BeautifulSoup
import re

class CryptoScraper:
    def __init__(self):
        self.vbr_url = "https://www.vbr.ru/crypto/"
        self.investing_url = "https://ru.investing.com/crypto"
        self.bitinfo_url = "https://bitinfocharts.com/ru/crypto-kurs/"

    @staticmethod
    def clean_price(price: str):
        price = re.sub(r'\.(?=.*\.)', '', price)  # Убираем лишние точки
        return price

    def get_vbr_data(self):
        response = requests.get(self.vbr_url)
        soup = BeautifulSoup(response.text, "html.parser")

        coins = soup.select('table tbody tr')
        vbr_data = {}

        for coin in coins:
            name_tag = coin.select_one('td:nth-child(1) span')
            price_tag = coin.select_one('td:nth-child(3) div')

            if name_tag and price_tag:
                name = name_tag.text.strip()
                price = price_tag.text.replace(' $', '').strip()
                vbr_data[name] = price

        return vbr_data

    def get_investing_data(self):
        response = requests.get(self.investing_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table_rows = soup.select('div:nth-of-type(5) > div > div:nth-of-type(2) > div:nth-of-type(1) > table > tbody > tr')

        investing_data = {}
        for row in table_rows:
            try:
                currency_name = row.select_one('td:nth-of-type(3)').get_text(strip=True)
                numeric_value = row.select_one('td:nth-of-type(4) > span').get_text(strip=True)
                investing_data[currency_name] = numeric_value
            except Exception:
                continue

        return investing_data

    def get_bitinfo_data(self):
        response = requests.get(self.bitinfo_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.select('table tbody tr')

        bitinfo_data = {}
        for row in rows:
            try:
                currency_name = row.select_one('td:nth-of-type(1)').text.strip()
                short_name = currency_name.split()[0]
                price = row.select_one('td:nth-of-type(2) a').text.strip()
                price = re.sub(r'[^\d.]', '', price)
                bitinfo_data[short_name] = price
            except Exception:
                continue

        return bitinfo_data

class CryptoDataProcessor:
    def __init__(self, scraper):
        self.scraper = scraper

    def get_crypto_prices(self):
        vbr_data = self.scraper.get_vbr_data()
        investing_data = self.scraper.get_investing_data()
        bitinfo_data = self.scraper.get_bitinfo_data()

        # print(f"VBR данные: {vbr_data}")  # 🔥 Лог
        # print(f"Investing данные: {investing_data}")  # 🔥 Лог
        # print(f"Bitinfo данные: {bitinfo_data}")  # 🔥 Лог

        common_currencies = set(vbr_data.keys()) & set(investing_data.keys()) & set(bitinfo_data.keys())

        desired_order = ["SOL", "BTC", "LINK", "DOGE", "ADA", "BNB", "LTC", "ETH", "XRP"]
        crypto_prices = []

        for currency in desired_order:
            if currency in common_currencies:
                vbr_price = self.scraper.clean_price(vbr_data[currency].replace(',', '.'))
                investing_price = self.scraper.clean_price(investing_data[currency].replace(',', '.'))
                bitinfo_price = self.scraper.clean_price(bitinfo_data[currency].replace(',', '.'))

                crypto_prices.append({
                    "currency": currency,
                    "vbr_price": vbr_price,
                    "investing_price": investing_price,
                    "bitinfo_price": bitinfo_price
                })
        print(f"Финальные данные: {crypto_prices}")  # 🔥 Лог

        return crypto_prices
