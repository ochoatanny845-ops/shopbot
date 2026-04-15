import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
import requests, hashlib, urllib.parse
from collections import OrderedDict

shop_id = "31439"
shop_token = "9VdfeDiGoUXRuv5ACE1MbFhL0tr47Za"

data = {'id': shop_id}
data = OrderedDict(sorted(data.items()))
query = urllib.parse.unquote(urllib.parse.urlencode(data, quote_via=urllib.parse.quote))
sign_str = query + '&token=' + shop_token
data['sign'] = hashlib.md5(sign_str.encode()).hexdigest().upper()

print('Request:', dict(data))
print('Sign string:', sign_str)

r = requests.post('https://api.okaypay.me/shop/balance', data=data, timeout=5)
print('Response:', r.json())
