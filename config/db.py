from pymongo import MongoClient


class DatabaseConnection:
    package_permissions_collection = None
    package_apks_collection = None
    internet_packages_collection = None
    notifications_collection = None
    access_tokens_collection = None
    users_collection = None
    blog_posts_collection = None

    @staticmethod
    def initializeConnection():
        db_connection = MongoClient("mongodb://127.0.0.1:27017")
        db = db_connection.netwatch_pro_db
        DatabaseConnection.package_permissions_collection = db['package_permissions']
        DatabaseConnection.package_apks_collection = db['package_apks']
        DatabaseConnection.internet_packages_collection = db['internet_packages']
        DatabaseConnection.notifications_collection = db['notifications']
        DatabaseConnection.access_tokens_collection = db['access_tokens']
        DatabaseConnection.users_collection = db['users']
        DatabaseConnection.blog_posts_collection = db['blog_posts']

    @staticmethod
    def get_package_permissions_collection():
        return DatabaseConnection.package_permissions_collection

    @staticmethod
    def get_package_apks_collection():
        return DatabaseConnection.package_apks_collection

    @staticmethod
    def get_internet_packages_collection():
        return DatabaseConnection.internet_packages_collection

    @staticmethod
    def get_notifications_collection():
        return DatabaseConnection.notifications_collection

    @staticmethod
    def get_access_tokens_collection():
        return DatabaseConnection.access_tokens_collection

    @staticmethod
    def get_users_collection():
        return DatabaseConnection.users_collection

    @staticmethod
    def get_blog_posts_collection():
        return DatabaseConnection.blog_posts_collection


# Usage
DatabaseConnection.initializeConnection()
permissions_collection = DatabaseConnection.get_package_permissions_collection()
