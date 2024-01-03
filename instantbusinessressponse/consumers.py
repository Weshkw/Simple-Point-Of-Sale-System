import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.shortcuts import get_object_or_404
from .models import Sale, Product

class SalesConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)
        sale_data = data['sale_data']

        # Get the username from the data
        username = sale_data.get('username')

        # Use sync_to_async for the synchronous database operation
        product = await sync_to_async(get_object_or_404)(Product, product_name=sale_data['product_name'])

        # Create a Sale instance related to the product and user
        sale_instance = await sync_to_async(Sale.objects.create)(
            user=self.scope["user"],  # Assuming the user is authenticated
            product=product,
            sale_price=sale_data['product_price'],
            sale_name=sale_data['product_name'],
        )

        # Broadcast the sale instance to all connected clients
        await self.send(text_data=json.dumps({
            'type': 'record_sale',
            'sale_data': {
                'sale_name': sale_instance.sale_name,
                'sale_price': sale_instance.sale_price,
                'username': username,
                'success': True,  # or False based on the result of the sale
                'product_name': sale_instance.product.product_name,
                'product_price': sale_instance.sale_price,
                # Add other fields you want to broadcast
            }
        }))
