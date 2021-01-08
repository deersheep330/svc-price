import datetime
import requests
import grpc

from api.protos import database_pb2_grpc
from api.protos.database_pb2 import StockPrice
from api.protos.protobuf_datatype_utils import datetime_to_timestamp
from price.utils import get_api_token, get_grpc_hostname


class TwPriceParser():

    def __init__(self):

        self.token = get_api_token()

        channel = grpc.insecure_channel(f'{get_grpc_hostname()}:6565')
        self.stub = database_pb2_grpc.DatabaseStub(channel)

        self.__reset__()

    def __reset__(self):
        self.symbol = None
        self.price_open = None
        self.price_close = None
        self.datetime = None

    def parse(self, symbol):

        self.__reset__()

        try:
            self.symbol = symbol
            url = f'https://api.fugle.tw/realtime/v0/intraday/quote?symbolId={self.symbol}&apiToken={self.token}'

            print(f'==> parse url: {url}')
            resp = requests.get(url)
            json = resp.json()
            self.price_open = float(json['data']['quote']['priceOpen']['price'])
            self.price_close = float(json['data']['quote']['trade']['price'])
            self.datetime = json['data']['quote']['priceOpen']['at']
            self.datetime = datetime.datetime.strptime(self.datetime, '%Y-%m-%dT%H:%M:%S.%fZ')

            print(f'{self.symbol} {self.price_open} {self.price_close} {self.datetime}')
        except Exception as e:
            print(e)
        finally:
            return self

    def save_to_db(self):

        if self.symbol is None or self.price_open is None or self.price_close is None or self.datetime is None:
            print('cannot write missing data to db')
            return

        # insert open price
        timestamp = datetime_to_timestamp(self.datetime)
        _dict = {
            'symbol': self.symbol,
            'date': timestamp,
            'price': self.price_open
        }
        try:
            rowcount = self.stub.insert_twse_open_price(StockPrice(
                symbol=_dict['symbol'],
                date=_dict['date'],
                price=_dict['price']
            ))
            print(rowcount)
        except grpc.RpcError as e:
            status_code = e.code()
            print(e.details())
            print(status_code.name, status_code.value)

        # insert close price
        _dict['price'] = self.price_close
        try:
            rowcount = self.stub.insert_twse_close_price(StockPrice(
                symbol=_dict['symbol'],
                date=_dict['date'],
                price=_dict['price']
            ))
            print(rowcount)
        except grpc.RpcError as e:
            status_code = e.code()
            print(e.details())
            print(status_code.name, status_code.value)