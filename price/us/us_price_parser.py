from dateutil import parser, tz
import requests
from lxml import etree

class UsPriceParser():

    def __init__(self):
        self.__reset__()

    def __reset__(self):
        self.symbol = None
        self.price = None
        self.date = None

    def parse(self, symbol):

        try:
            self.symbol = symbol
            url = f'https://www.marketwatch.com/investing/stock/{self.symbol}'

            print(f'==> parse url: {url}')
            resp = requests.get(url, timeout=60)
            resp.raise_for_status()
            content = resp.text
            tree = etree.HTML(content)

            dates = tree.xpath("//*[contains(@field, 'date')]")
            prices = tree.xpath("//*[contains(@field, 'Last')]")

            if len(dates) == 0 or len(prices) == 0:
                raise Exception(f'cannot get date or price for {self.symbol}')

            self.date = parser.parse(dates[0].text)
            self.date = self.date.replace(tzinfo=tz.gettz('America/New_York'))
            self.date = self.date.astimezone(tz.gettz('Asia/Taipei'))

            self.price = prices[0].text

            print(f'{self.symbol} {self.price} {self.date}')
        except Exception as e:
            print(e)
