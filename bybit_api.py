import hashlib
import hmac
import time
import requests
import json
import pprint
from config import BYBIT_API_KEY, BYBIT_SECRET_KEY

class BybitApi:
    BASE_LINK = "https://api.bybit.com"

    def __init__(self, api_key='test', secret_key='test', futures=False):
        self.api_key = api_key
        self.secret_key = secret_key
        self.futures = futures
        if self.futures:
            self.category = "linear"
        else:
            self.category = "spot"
        self.header = {
            'X-BAPI-API-KEY': self.api_key,
            "X-BAPI-RECV-WINDOW": "5000",
        }


    def _gen_signature(self, mod_params, timestamp):
        param_str = timestamp + self.api_key + '5000' + mod_params
        sign = hmac.new(bytes(self.secret_key, "utf-8"), param_str.encode("utf-8"), hashlib.sha256).hexdigest()
        return sign

    def _http_request(self, method, endpoint, params):
        """
        Sends http request to the trading platform server

        :param endpoint: request url
        :param method: request type (GET, POST)
        :param params: request body (params)

        :return: :class:Response (requests.models.Response)
        """
        timestamp = str(int(time.time() * 1000))
        if method == 'GET':
            params_get_string = '&'.join([f'{k}={v}' for k, v in params.items()])
            sign = self._gen_signature(params_get_string, timestamp)
            self.header['X-BAPI-SIGN'] = sign
            self.header['X-BAPI-TIMESTAMP'] = timestamp
            response = requests.get(url=self.BASE_LINK + endpoint, params=params, headers=self.header)
        elif method == "POST":
            params_post_json = json.dumps(params)
            sign = self._gen_signature(params_post_json, timestamp)
            self.header['X-BAPI-SIGN'] = sign
            self.header['X-BAPI-TIMESTAMP'] = timestamp
            response = requests.post(url=self.BASE_LINK + endpoint, data=json.dumps(params), headers=self.header)
        else:
            print("Метод не известен!")
            return None

        if response:  # check if the answer is not empty - so as not to get an error when formatting an empty answer
            response = response.json()
        else:
            print(response.text)
        return response

    def get_tickers(self, symbol: str = None):
        endpoint = "/v5/market/tickers"
        method = "GET"
        params = {
            'category': self.category,
        }
        if symbol:
            params['symbol'] = symbol

        return self._http_request(method=method, endpoint=endpoint, params=params)

    def post_limit_order(self, symbol: str, side: str, qnt, price, reduce_only=False):
        endpoint = "/v5/order/create"
        method = "POST"
        params = {
            'category': self.category,
            'symbol': symbol,
            'side': side.capitalize(),
            'orderType': 'Limit',
            'qty': str(qnt),
            'price': str(price)
        }
        if reduce_only:
            params['reduceOnly'] = reduce_only

        return self._http_request(method=method, endpoint=endpoint, params=params)

    def post_cancel_order(self, symbol: str, orderId: str = None, orderLinkId: str = None):
        endpoint = "/v5/order/cancel"
        method = "POST"
        params = {
            'category': self.category,
            'symbol': symbol,
        }
        if orderId:
            params['orderId'] = orderId
        elif orderLinkId:
            params['orderLinkId'] = orderLinkId
        else:
            return print("No paramether orderId")

        return self._http_request(method=method, endpoint=endpoint, params=params)

    def get_orders_info(self, symbol: str = None, baseCoin: str = None, settleCoin: str = None, orderId: str = None,
                        orderLinkId: str = None, openOnly: int = 0):
        endpoint = "/v5/order/realtime"
        method = "GET"
        params = {
            'category': self.category,
        }
        if symbol:
            params['symbol'] = symbol
        if baseCoin:
            params['baseCoin'] = baseCoin
        if settleCoin:
            params['settleCoin'] = settleCoin
        if orderId:
            params['orderId'] = orderId
        if orderLinkId:
            params['orderLinkId'] = orderLinkId
        if openOnly:
            params['openOnly'] = openOnly

        return self._http_request(method=method, endpoint=endpoint, params=params)

    def get_instruments_info(self, symbol: str = None, status: str = None, baseCoin: str = None, limit: int = None):
        endpoint = "/v5/market/instruments-info"
        method = "GET"
        params = {
            'category': self.category,
        }
        if symbol:
            params['symbol'] = symbol
        if status:
            params['status'] = status
        if baseCoin:
            params['baseCoin'] = baseCoin
        if limit:
            params['limit'] = limit

        return self._http_request(method=method, endpoint=endpoint, params=params)
