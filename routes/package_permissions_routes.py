from fastapi import APIRouter, Form
from typing import Annotated, Optional
from models.package_permissions_model import PackagePermissions
from schemas.package_permissions_schema import all_package_permissions_serializer
from config.db import package_permissions_collection

package_permission = APIRouter()


@package_permission.post("/v1/package-permissions/add", status_code=201)
async def add_package_permission(
    device_token: Optional[str] = Form(None),
    package_name: Optional[str] = Form(None),
    app_name: Optional[str] = Form(None),
    permissions: Optional[str] = Form(None),
    certificate_subjects: Optional[str] = Form(None),
    certificate_issuers: Optional[str] = Form(None),
    certificate_serial_numbers: Optional[str] = Form(None),
    certificate_versions: Optional[str] = Form(None)
):
    package_permission_model = PackagePermissions(
        device_token=device_token,
        package_name=package_name,
        app_name=app_name,
        permissions=list(str(permissions).split(",")),
        certificate_subjects=list(str(certificate_subjects).split(",")),
        certificate_issuers=list(str(certificate_issuers).split(",")),
        certificate_serial_numbers=list(str(certificate_serial_numbers).split(",")),
        certificate_versions=list(str(certificate_versions).split(","))
    )
    _id = package_permissions_collection.insert_one(dict(package_permission_model))
    package_permission_details = all_package_permissions_serializer(
        package_permissions_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "package_permission": package_permission_details
    }
