from pprint import pprint
from datetime import datetime
from dateutil import parser, tz

import requests
from lxml import etree

url = 'https://www.marketwatch.com/investing/stock/TSM?mod=mw_quote_switch'

resp = requests.get(url, timeout=60)
resp.raise_for_status()
content = resp.text
tree = etree.HTML(content)

dates = tree.xpath("//*[contains(@field, 'date')]")
#date = datetime.strftime(dates[0].text, '%b ')
_date = parser.parse(dates[0].text)
_date = _date.replace(tzinfo=tz.gettz('America/New_York'))
_date = _date.astimezone(tz.gettz('Asia/Taipei'))
print(_date)
'''
price = tree.xpath("//*[contains(@field, 'Last')]")

# get stock info
print(symbols[0].text, dates[0].text, price[0].text)
'''