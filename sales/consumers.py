from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from .models import Product, Sale


class SalesConsumer(AsyncJsonWebsocketConsumer):
    """Records sales sent from the till page and confirms each one back.

    The client only says which product was sold; the price always comes from
    the catalogue so a modified page cannot record a sale at a made-up price.
    """

    async def connect(self):
        if self.scope["user"].is_authenticated:
            await self.accept()
        else:
            await self.close()

    async def receive_json(self, content, **kwargs):
        sale = await self.record_sale(content.get("product_id"))
        if sale is None:
            await self.send_json({"type": "sale_failed"})
            return
        await self.send_json(
            {
                "type": "sale_recorded",
                "sale": {"product_name": sale.sale_name, "sale_price": str(sale.sale_price)},
            }
        )

    @database_sync_to_async
    def record_sale(self, product_id):
        try:
            product = Product.objects.get(pk=int(product_id))
        except (TypeError, ValueError, Product.DoesNotExist):
            return None
        return Sale.record(user=self.scope["user"], product=product)
