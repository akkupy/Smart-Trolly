import json
from channels.generic.websocket import AsyncWebsocketConsumer

from asgiref.sync import async_to_sync

class CartConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.room_group_name = f'cart_{self.user_id}'
        # Join the WebSocket group (similar to a chat room)
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the WebSocket group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive a message from WebSocket
    async def receive(self, text_data):
        from db.models import Cart, CartItem
        text_data_json = json.loads(text_data)
        product_name = text_data_json['product_name']
        price = text_data_json['price']
        quantity = text_data_json['quantity']
        
        # Get or create the cart for the user
        cart, created = Cart.objects.get_or_create(user_id=self.user_id, purchased_at__isnull=True)

        # Create a cart item
        cart_item = CartItem.objects.create(
            cart=cart,
            product_name=product_name,
            price=price,
            quantity=quantity
        )

        # Fetch all cart items and prepare data for broadcast
        cart_items = [
            {
                'product_name': item.product_name,
                'quantity': item.quantity,
                'price': str(item.price),
                'total_item_price': str(item.total_item_price())
            }
            for item in cart.items.all()
        ]

        # Send message to WebSocket group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'cart_update',
                'cart_items': cart_items
            }
        )

    # Receive message from WebSocket group
    async def cart_update(self, event):
        cart_items = event['cart_items']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'cart_update',
            'cart_items': cart_items
        }))
