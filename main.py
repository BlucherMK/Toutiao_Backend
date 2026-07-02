from fastapi import FastAPI

from routers import favorite, news, users
from fastapi.middleware.cors import CORSMiddleware

from utils.exception_handlers import register_exception_handler
app = FastAPI()

register_exception_handler(app)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://your-frontend-domain.com",
    "http://localhost:5173"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
async def root():
    return{"message": "Hello World"}


#挂在路由/注册路由
app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)