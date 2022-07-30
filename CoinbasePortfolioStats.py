from coinbase.wallet.client import Client
import pandas as pd
from collections import defaultdict
coinbase_API_key = "Get your API key from coinbase account"
coinbase_API_secret = "Make sure to get your secret ket that only appears once"
client = Client(coinbase_API_key, coinbase_API_secret)

#iniliase next wallet id
next=None
# this loop wil run until next_uri parameter is none ( it means that there is no other page to show)
ids = []
currencies = []
amt_USD = []
amt_cryp = []

while len(currencies) < 10:
    accounts=client.get_accounts(starting_after=next)
    next=accounts.pagination.next_starting_after
    for i, wallet in enumerate(accounts.data):

        if wallet['native_balance']['amount'] != '0.00':
            # print(str(wallet['name']) + ' ' + str(wallet['native_balance']))
            ids.append(wallet["id"])
            currencies.append(wallet["currency"])
            amt_USD.append( float(wallet['native_balance']['amount']))
            amt_cryp.append(float(wallet["balance"]["amount"]))

        if accounts.pagination.next_uri==None :
            print("end")
            break


wallets = pd.DataFrame({"ids": ids, "currency": currencies, "USD_balance": amt_USD, "crypto_balance": amt_cryp})
#get transactions for each wallet
net_purchases = []
for id in ids:
    txs = client.get_transactions(id)
    total_spent = 0
    total_sold = 0
    for tx in txs["data"]:

        if( tx["type"] == "buy" ):
            total_spent+= float(tx["native_amount"]["amount"])
        elif( tx["type"] == "sell"):
            total_sold+=  float(tx["native_amount"]["amount"])
    net_total = total_spent - total_sold
    net_purchases.append(net_total)
wallets["total_net_purchases"] = net_purchases

def compute_stats(df):

    df = df[df["total_net_purchases"] > 0 ]
    df['percent_return'] =  100 * (df['USD_balance'] -df['total_net_purchases'])  / df['total_net_purchases']
    df['avg_cost_of_coin'] = df['total_net_purchases'] / df['crypto_balance']
    df['curr_cost_of_coin'] = [client.get_buy_price(currency_pair = f"{currency}-USD")["amount"] for currency in currencies if currency in df["currency"].tolist()]
    # df = df[df["currency"] != "USDC"]
    print(df)
    net_total = df["total_net_purchases"].sum()
    total_worth = df["USD_balance"].sum()
    print("Total Spent", net_total)
    print("Total Worth", total_worth)
    print("Total Return",  ((total_worth-net_total) / net_total) * 100)

compute_stats(wallets)




# import hashlib
# import hmac
# import json
# from datetime import datetime

# import pandas
# from requests import get
# from requests.auth import AuthBase

# URL = 'https://api.coinbase.com'

# class Auth(AuthBase):
#     VERSION = b'2021-03-30'

#     def __init__(self, API_KEY, API_SECRET):
#         self.API_KEY = API_KEY
#         self.API_SECRET = API_SECRET

#     def __call__(self, request):
#         timestamp = datetime.now().strftime('%s')
#         message = f"{timestamp}{request.method}{request.path_url}{request.body or ''}"
#         signature = hmac.new(self.API_SECRET.encode(),
#                              message.encode('utf-8'),
#                              digestmod=hashlib.sha256)
#         signature_hex = signature.hexdigest()

#         request.headers.update({
#             'CB-ACCESS-SIGN': signature_hex,
#             'CB-ACCESS-TIMESTAMP': timestamp.encode(),
#             'CB-ACCESS-KEY': self.API_KEY.encode(),
#             'CB-VERSION': self.VERSION,
#             'Content-Type': 'application/json'
#         })
#         return request


# class Coinbase:
#     df_accounts = None

#     def __init__(self, API_KEY, API_SECRET):
#         self.API_KEY = API_KEY
#         self.API_SECRET = API_SECRET
#         self._accounts()

#     def _request(self, request_path):
#         auth = Auth(self.API_KEY, self.API_SECRET)
#         return get(f'{URL}{request_path}', auth=auth)

#     def _accounts(self):
#         request_path = '/v2/accounts'
#         r = self._request(request_path)
#         df = pandas.json_normalize(json.loads(r.content)['data'])
#         df = df[['id', 'balance.amount','balance.currency']]
#         self.df_accounts = df.loc[df['id'] != df['balance.currency'] ]

#     def _get_transactions(self, id):
#         request_path = f'/v2/accounts/{id}/transactions'
#         r = self._request(request_path)
#         df = pandas.json_normalize(json.loads(r.content)['data'])
#         return df

#     def transactions(self):
#         df_tr = []
#         for i in self.df_accounts.index:
#             df_tr.append(self._get_transactions(self.df_accounts['id'][i]))
#         df = pandas.concat(df_tr, ignore_index=True)
#         return df

# Coins = Coinbase(coinbase_API_key, coinbase_API_secret)
# print(Coins.df_accounts)


