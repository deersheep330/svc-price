from price.us import UsPriceParser
from price.tw import TwPriceParser

if __name__ == '__main__':

    # ptt 7 days => close price
    # reunion 7 days => close price

    # twse over bought / sold 1 day => open price

    us_price_parser = UsPriceParser()
    us_price_parser.parse('TSM').save_to_db()

    tw_price_parser = TwPriceParser()
    tw_price_parser.parse('2603').save_open_price_to_db()
    tw_price_parser.parse('2609').save_close_price_to_db()
