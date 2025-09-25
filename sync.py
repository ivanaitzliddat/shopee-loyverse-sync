import logging
from datetime import datetime, timedelta
from db import SessionLocal
from models import ProductMapping, ProcessedOrder, SyncLog
from connectors.shopee_connector import ShopeeClient
from connectors.loyverse_connector import LoyverseClient
from utils import logger
from settings import settings

class SyncService:
    def __init__(self):
        self.shopee = ShopeeClient()
        self.loyverse = LoyverseClient()
        self.db = SessionLocal()

    def log(self, level, message, meta=None):
        logger.info(message)
        log = SyncLog(level=level, message=message, meta=meta or {})
        self.db.add(log)
        self.db.commit()

    def sync_shopee_orders(self):
        # 1. Pull orders from last X minutes
        now = int(datetime.utcnow().timestamp())
        since = int((datetime.utcnow() - timedelta(seconds=settings.SCHEDULE_INTERVAL_SECONDS*2)).timestamp())
        resp = self.shopee.get_orders(create_time_from=since, create_time_to=now)
        orders = resp.get("response", {}).get("order_list", []) if isinstance(resp, dict) else []
        for o in orders:
            order_sn = o.get("order_sn") or o.get("order_id") or o.get("order_number")
            if not order_sn:
                continue
            # idempotency: skip if processed
            exists = self.db.query(ProcessedOrder).filter_by(order_id=order_sn).first()
            if exists:
                continue
            try:
                self._process_shopee_order(o)
                # mark processed
                po = ProcessedOrder(order_id=order_sn, source="shopee", raw=o)
                self.db.add(po); self.db.commit()
            except Exception as e:
                self.log("ERROR", f"Failed processing order {order_sn}: {e}", {"order": o})

    def _process_shopee_order(self, order):
        """
        Create a Loyverse receipt and reduce stock accordingly.
        Order structure may need parsing; adapt to Shopee response.
        """
        # map shopee item -> sku -> loyverse item id
        line_items = []
        for item in order.get("items", []):
            sku = item.get("model_sku") or item.get("sku") or item.get("item_sku")
            quantity = int(item.get("model_quantity") or item.get("quantity") or 1)
            price = float(item.get("price", 0)) / 1000000 if "price" in item else float(item.get("original_price", 0))
            mapping = self.db.query(ProductMapping).filter_by(sku=sku).first()
            if not mapping or not mapping.loyverse_item_id:
                raise Exception(f"No Loyverse mapping for SKU {sku}")
            # Build loyverse line item structure (adapt to API)
            line_items.append({
                "item_id": mapping.loyverse_item_id,
                "quantity": quantity,
                "price": price
            })
        receipt_payload = {"receipts": [{"line_items": line_items, "created_at": datetime.utcnow().isoformat()}]}
        resp = self.loyverse.create_receipt(receipt_payload)
        self.log("INFO", f"Created receipt for Shopee order {order.get('order_sn')}", {"receipt_resp": resp})

    def sync_stock_to_shopee(self):
        """
        Read inventory from Loyverse and push to Shopee using mapping table
        """
        # fetch loyverse items (paged)
        offset = 0; limit = 100
        while True:
            res = self.loyverse.get_items(limit=limit, offset=offset)
            items = res.get("items", [])
            if not items:
                break
            for item in items:
                sku = item.get("code") or item.get("sku") or item.get("item_code")
                in_stock = item.get("stock") or item.get("in_stock") or item.get("inventory", 0)
                mapping = self.db.query(ProductMapping).filter_by(sku=sku).first()
                if mapping and mapping.shopee_item_id:
                    # For multi-variation, construct variation list (this is an example)
                    stocks = [{"variation_id": mapping.extra.get("variation_id"), "stock": in_stock}]
                    try:
                        self.shopee.update_stock(mapping.shopee_item_id, stocks)
                        self.log("INFO", f"Updated Shopee stock for SKU {sku}", {"shopee_item_id": mapping.shopee_item_id, "stock": in_stock})
                    except Exception as e:
                        self.log("ERROR", f"Failed updating Shopee stock for SKU {sku}: {e}")
                else:
                    self.log("WARN", f"No mapping for SKU {sku}; skipping Shopee stock update")
            offset += limit

    def run_once(self):
        try:
            self.sync_shopee_orders()
            self.sync_stock_to_shopee()
        except Exception as e:
            self.log("ERROR", f"Sync run failed: {e}")
