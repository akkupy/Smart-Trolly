import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smart_trolly.settings')

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path
from web.consumers import CartConsumer

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('ws/cart/<int:user_id>/', CartConsumer.as_asgi()),
        ])
    ),
})