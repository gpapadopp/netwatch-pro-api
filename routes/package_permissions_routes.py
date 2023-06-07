from fastapi import APIRouter
from models.package_permissions_model import PackagePermissions
from schemas.package_permissions_schema import all_package_permissions_serializer
from config.db import package_permissions_collection

package_permission = APIRouter()


@package_permission.post("/api/v1/package-permissions/add", status_code=201)
async def add_package_permission(package_permission_details: PackagePermissions):
    _id = package_permissions_collection.insert_one(dict(package_permission_details))
    package_permission_details = all_package_permissions_serializer(
        package_permissions_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "package_permission": package_permission_details
    }
