import time, hashlib, hmac, json
import requests
from settings import settings
from utils import retry_decorator, logger

class ShopeeClient:
    def __init__(self):
        self.base = settings.SHOPEE_API_BASE
        self.partner_id = str(settings.SHOPEE_PARTNER_ID)
        self.partner_key = settings.SHOPEE_PARTNER_KEY
        self.shop_id = str(settings.SHOPEE_SHOP_ID)

    def _sign(self, path: str, timestamp: int):
        # Shopee partner sign = HMAC_SHA256(partner_key, partner_id + path + timestamp)
        base_string = f"{self.partner_id}{path}{timestamp}"
        signature = hmac.new(self.partner_key.encode(), base_string.encode(), hashlib.sha256).hexdigest()
        return signature

    def _url(self, path: str, timestamp: int, sign: str):
        return f"{self.base}{path}?partner_id={self.partner_id}&timestamp={timestamp}&shop_id={self.shop_id}&sign={sign}"

    @retry_decorator()
    def _post(self, path: str, payload: dict):
        ts = int(time.time())
        sig = self._sign(path, ts)
        url = self._url(path, ts, sig)
        resp = requests.post(url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry_decorator()
    def _get(self, path: str, params=None):
        ts = int(time.time())
        sig = self._sign(path, ts)
        url = self._url(path, ts, sig)
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    # Example: get order list
    def get_orders(self, create_time_from=None, create_time_to=None):
        path = "/order/get_order_list"
        payload = {"pagination_offset": 0, "pagination_entries_per_page": 50}
        if create_time_from:
            payload["create_time_from"] = create_time_from
        if create_time_to:
            payload["create_time_to"] = create_time_to
        return self._post(path, payload)

    def get_order_detail(self, order_sn):
        path = "/order/get_order_detail"
        payload = {"order_sn_list": [order_sn]}
        return self._post(path, payload)

    def update_stock(self, item_id, stocks):
        """
        stocks: list of dicts [{'variation_id': <id>, 'stock': <int>}, ...]
        """
        path = "/product/update_stock"
        payload = {"item_id": item_id, "stock_list": stocks}
        return self._post(path, payload)

    # Add more Shopee endpoints as needed
