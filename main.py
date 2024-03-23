from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.package_permissions_routes import package_permission
from routes.package_apks_routes import package_apk
from routes.internet_packages_routes import internet_package
from routes.notifications_routes import notification_api
from routes.access_tokens_routes import access_token_api
from routes.users_routes import users_api
from routes.blog_posts_routes import blog_post_api
from config.db import DatabaseConnection

DatabaseConnection.initializeConnection()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your needs
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Adjust this to your needs
    allow_headers=["*"],  # Adjust this to your needs
)

app.include_router(package_permission)
app.include_router(package_apk)
app.include_router(internet_package)
app.include_router(notification_api)
app.include_router(access_token_api)
app.include_router(users_api)
app.include_router(blog_post_api)
