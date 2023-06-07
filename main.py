from fastapi import FastAPI
from routes.package_permissions_routes import package_permission

app = FastAPI()

app.include_router(package_permission)