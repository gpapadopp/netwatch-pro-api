from fastapi import APIRouter, Form
from typing import Annotated, Optional
from enums.access_models_enum import AccessModelsEnum
from models.internet_packages_model import InternetPackages
from schemas.internet_packages_schema import all_internet_packages_serializer
from config.db import DatabaseConnection
from responses.internet_packages_responses import InternetPackagesAdd
from utils.permission_checker import PermissionChecker

internet_package = APIRouter()
permission_access_checker = PermissionChecker()


@internet_package.post("/v1/internet-packages/add", status_code=201, tags=['Internet Packages'], summary="Add Internet Package", description="Add an Internet Package", response_model=InternetPackagesAdd)
async def add_internet_package(
    device_token: Annotated[str, Form()],
    source_ip: Annotated[str, Form()],
    destination_ip: Annotated[str, Form()],
    source_mac_address: Annotated[str, Form()],
    destination_mac_address: Annotated[str, Form()],
    header_type: Annotated[str, Form()],
    raw_header: Annotated[str, Form()],
    raw_payload: Annotated[str, Form()],
    api_key: Optional[str] = Form(None),
    secret_key: Optional[str] = Form(None),
):
    if api_key is None or secret_key is None:
        return InternetPackagesAdd(success=False, message="unauthorized", internet_package=None)

    if not permission_access_checker.check_model_permission(AccessModelsEnum.PackageAPKsModel, api_key, secret_key):
        return InternetPackagesAdd(success=False, message="unauthorized", internet_package=None)

    current_access_token = DatabaseConnection.get_access_tokens_collection().find_one({"api_key": api_key, "secret_key": secret_key})

    internet_package_model = InternetPackages(
        device_token=device_token,
        source_ip=source_ip,
        destination_ip=destination_ip,
        source_mac_address=source_mac_address,
        destination_mac_address=destination_mac_address,
        header_type=header_type,
        raw_header=raw_header,
        raw_payload=raw_payload,
        access_token_id=str(current_access_token['_id'])
    )

    _id = DatabaseConnection.get_internet_packages_collection().insert_one(dict(internet_package_model))
    internet_package_details_db = all_internet_packages_serializer(
        DatabaseConnection.get_internet_packages_collection().find({"_id": _id.inserted_id}))
    return InternetPackagesAdd(success=True, message=None, internet_package=internet_package_details_db[0])
