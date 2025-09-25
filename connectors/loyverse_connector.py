import requests
from settings import settings
from utils import retry_decorator, logger

class LoyverseClient:
    def __init__(self):
        self.base = settings.LOYVERSE_API_BASE
        self.token = settings.LOYVERSE_TOKEN
        self.headers = {"Authorization": f"Bearer {self.token}", "Content-Type": "application/json"}

    @retry_decorator()
    def get_inventory(self, limit=100, offset=0):
        url = f"{self.base}/inventories?limit={limit}&offset={offset}"
        resp = requests.get(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry_decorator()
    def create_receipt(self, receipt_payload):
        """
        Build payload according to Loyverse API for creating receipts.
        """
        url = f"{self.base}/receipts"
        resp = requests.post(url, headers=self.headers, json=receipt_payload, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry_decorator()
    def get_items(self, limit=100, offset=0):
        url = f"{self.base}/items?limit={limit}&offset={offset}"
        resp = requests.get(url, headers=self.headers, timeout=30)
        resp.raise_for_status()
        return resp.json()

    @retry_decorator()
    def update_stock(self, item_id, stock_change):
        # Loyverse may have endpoints to adjust stock by business logic
        # If Loyverse doesn't provide direct update, you may create inventory adjustments via its API
        url = f"{self.base}/inventories/adjustments"
        payload = {
            "item_id": item_id,
            "quantity": stock_change
        }
        resp = requests.post(url, headers=self.headers, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
