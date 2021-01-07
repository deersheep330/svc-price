from pprint import pprint

import requests
from lxml import etree

class UsPriceGetter():

    def __init__(self):
        pass

url = 'https://www.marketwatch.com/investing/stock/TSM?mod=mw_quote_switch'

resp = requests.get(url, timeout=60)
resp.raise_for_status()
content = resp.text
tree = etree.HTML(content)

symbols = tree.xpath("//*[contains(@class, 'intraday__close')]//*[contains(@class, 'table__cell')][1]")


# get stock info
pprint(symbols[0].text)