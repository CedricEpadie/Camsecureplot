import os
import django
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
from messagerie import routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()  # 👈 important avant d'importer routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)),
})
