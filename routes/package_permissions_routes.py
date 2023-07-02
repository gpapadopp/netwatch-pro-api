from fastapi import APIRouter, Form
from typing import Annotated
from models.package_permissions_model import PackagePermissions
from schemas.package_permissions_schema import all_package_permissions_serializer
from config.db import package_permissions_collection
from typing import Optional

package_permission = APIRouter()


@package_permission.post("/api/v1/package-permissions/add", status_code=201)
async def add_package_permission(
        device_token: Annotated[str, Form()],
        package_name: Annotated[str, Form()],
        app_name: Annotated[str, Form()],
        permissions: Annotated[Optional[str], Form()],
        certificate_subjects: Annotated[Optional[str], Form()],
        certificate_issuers: Annotated[Optional[str], Form()],
        certificate_serial_numbers: Annotated[Optional[str], Form()],
        certificate_versions: Annotated[Optional[str], Form()]
):
    all_permissions = []
    if permissions != "null" and permissions != "":
        all_permissions = str(permissions).split(",")

    all_certificate_subjects = []
    if certificate_subjects != "null" and certificate_subjects != "":
        all_certificate_subjects = str(certificate_subjects).split(",")

    all_certificate_issuers = []
    if certificate_issuers != "null" and certificate_issuers != "":
        all_certificate_issuers = str(certificate_issuers).split(",")

    all_certificate_serial_numbers = []
    if certificate_serial_numbers != "null" and certificate_serial_numbers != "":
        all_certificate_serial_numbers = str(certificate_serial_numbers).split(",")

    all_certificate_versions = []
    if certificate_versions != "null" and certificate_versions != "":
        all_certificate_versions = str(certificate_versions).split(",")

    package_permission_model = PackagePermissions(
        device_token=device_token,
        package_name=package_name,
        app_name=app_name,
        permissions=list(all_permissions),
        certificate_subjects=list(all_certificate_subjects),
        certificate_issuers=list(all_certificate_issuers),
        certificate_serial_numbers=list(all_certificate_serial_numbers),
        certificate_versions=list(all_certificate_versions)
    )
    _id = package_permissions_collection.insert_one(dict(package_permission_model))
    package_permission_details = all_package_permissions_serializer(
        package_permissions_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "package_permission": package_permission_details
    }
