from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.redis_connection import redis
from routers import items_router, users_router, admin_router
from middlewares.rate_limit_middleware import RateLimitMiddleware
import ssl

app = FastAPI()

ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
ssl_context.load_cert_chain('./cert.pem', keyfile='./key.pem')

app.add_middleware(RateLimitMiddleware)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    redis


@app.on_event("shutdown")
async def shutdown():
    await redis.close()


app.include_router(admin_router.router)
app.include_router(items_router.router)
app.include_router(users_router.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000, ssl=ssl_context)
