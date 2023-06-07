from fastapi import FastAPI
from routes.package_permissions_routes import package_permission

app = FastAPI()

app.include_router(package_permission)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
