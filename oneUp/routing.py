from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import Chat.routing
import Trivia.routing

routing = Chat.routing.websocket_urlpatterns + Trivia.routing.websocket_urlpatterns

print(routing)
application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            routing
        )
    ),
})