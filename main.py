from fastapi import FastAPI
from routes.package_permissions_routes import package_permission
from routes.package_apks_routes import package_apk
from routes.internet_packages_routes import internet_package
from routes.notifications_routes import notification_api
from routes.access_tokens_routes import access_token_api
from routes.users_routes import users_api

app = FastAPI()

app.include_router(package_permission)
app.include_router(package_apk)
app.include_router(internet_package)
app.include_router(notification_api)
app.include_router(access_token_api)
app.include_router(users_api)
