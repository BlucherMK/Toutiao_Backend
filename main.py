from fastapi import FastAPI

from routers import news, users

app = FastAPI()
#挂在路由/注册路由
app.include_router(news.router)
app.include_router(users.router)

@app.get("/")
async def root():
    return{"message": "Hello World"}

@app.get("/hello/{name}")
async def hello_name(name: str):
    return{"message": f"hello {name}"}