from price.us import UsPriceParser
from price.tw import TwPriceParser

if __name__ == '__main__':

    us_price_parser = UsPriceParser()
    us_price_parser.parse('TSM').save_to_db()

    tw_price_parser = TwPriceParser()
    tw_price_parser.parse('2330').save_to_db()
