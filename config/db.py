from pymongo import MongoClient

db_connection = MongoClient("mongodb://127.0.0.1:27017")
db = db_connection.netwatch_pro_db

# Package Permissions - Collection
package_permissions_collection = db['package_permissions']

# Package APKs - Collection
package_apks_collection = db['package_apks']

#Intener Packages - Collection
internet_packages_collection = db['internet_packages']
