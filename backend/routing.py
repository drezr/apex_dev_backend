import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from apex import consumers


application = ProtocolTypeRouter({
    'websocket': AuthMiddlewareStack(
        URLRouter([
            # re_path(r'ws/room/(?P<room_name>\w+)/$', consumers.RoomConsumer.as_asgi()),
        ])
    ),
})