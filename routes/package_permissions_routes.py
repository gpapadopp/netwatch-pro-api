from fastapi import APIRouter, Form
from typing import Annotated
from models.package_permissions_model import PackagePermissions
from schemas.package_permissions_schema import all_package_permissions_serializer
from config.db import package_permissions_collection

package_permission = APIRouter()


@package_permission.post("/api/v1/package-permissions/add", status_code=201)
async def add_package_permission(
    device_token: Annotated[str, Form()],
    package_name: Annotated[str, Form()],
    app_name: Annotated[str, Form()],
    permissions: Annotated[list, Form()],
    certificate_subjects: Annotated[list, Form()],
    certificate_issuers: Annotated[list, Form()],
    certificate_serial_numbers: Annotated[list, Form()],
    certificate_versions: Annotated[list, Form()]
):
    package_permission_model = PackagePermissions(
        device_token=device_token,
        package_name=package_name,
        app_name=app_name,
        permissions=permissions,
        certificate_subjects=certificate_subjects,
        certificate_issuers=certificate_issuers,
        certificate_serial_numbers=certificate_serial_numbers,
        certificate_versions=certificate_versions
    )
    _id = package_permissions_collection.insert_one(dict(package_permission_model))
    package_permission_details = all_package_permissions_serializer(
        package_permissions_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "package_permission": package_permission_details
    }
