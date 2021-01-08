from dateutil import parser, tz
import requests
from lxml import etree
import grpc

from api.protos import database_pb2_grpc
from api.protos.database_pb2 import StockPrice
from api.protos.protobuf_datatype_utils import datetime_to_timestamp
from price.utils import get_grpc_hostname

class UsPriceParser():

    def __init__(self):
        channel = grpc.insecure_channel(f'{get_grpc_hostname()}:6565')
        self.stub = database_pb2_grpc.DatabaseStub(channel)
        self.__reset__()

    def __reset__(self):
        self.symbol = None
        self.price = None
        self.datetime = None

    def parse(self, symbol):

        self.__reset__()

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

            self.datetime = parser.parse(dates[0].text)
            self.datetime = self.datetime.replace(tzinfo=tz.gettz('America/New_York'))
            self.datetime = self.datetime.astimezone(tz.gettz('Asia/Taipei'))

            self.price = float(prices[0].text)

            print(f'{self.symbol} {self.price} {self.datetime}')
        except Exception as e:
            print(e)
        finally:
            return self

    def save_to_db(self):

        if self.symbol is None or self.price is None or self.datetime is None:
            print('cannot write missing data to db')
            return

        timestamp = datetime_to_timestamp(self.datetime)
        _dict = {
            'symbol': self.symbol,
            'date': timestamp,
            'price': self.price
        }
        try:
            rowcount = self.stub.insert_us_close_price(StockPrice(
                symbol=_dict['symbol'],
                date=_dict['date'],
                price=_dict['price']
            ))
            print(rowcount)
        except grpc.RpcError as e:
            status_code = e.code()
            print(e.details())
            print(status_code.name, status_code.value)
