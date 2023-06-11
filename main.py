from fastapi import FastAPI
from routes.package_permissions_routes import package_permission
from routes.package_apks_routes import package_apk
from routes.internet_packages_routes import internet_package

app = FastAPI()

app.include_router(package_permission)
app.include_router(package_apk)
app.include_router(internet_package)
