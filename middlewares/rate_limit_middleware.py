from starlette.types import ASGIApp, Scope, Receive, Send
from starlette.responses import PlainTextResponse
from utils.leaky_bucket import leaky_bucket


class RateLimitMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope['type'] != 'http':
            await self.app(scope, receive, send)
            return

        client_ip = scope["client"][0] if scope["client"] else "unknown"

        if not await leaky_bucket(client_ip):
            response = PlainTextResponse(
                "Rate limit exceeded", status_code=429)
            await response(scope, receive, send)
        else:
            await self.app(scope, receive, send)
