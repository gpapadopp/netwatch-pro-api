from fastapi import APIRouter, Form, Query, Header
from typing import Annotated, Optional
from enums.access_models_enum import AccessModelsEnum
from models.internet_packages_model import InternetPackages
from schemas.internet_packages_schema import all_internet_packages_serializer
from config.db import DatabaseConnection
import utils.users_auth
from responses.internet_packages_responses import InternetPackagesResponseAdd
from responses.internet_packages_responses import InternetPackagesResponseIndex
from responses.internet_packages_responses import InternetPackagesResponseView
from responses.internet_packages_responses import InternetPackagesResponseUpdate
from responses.internet_packages_responses import InternetPackagesResponseDelete
from response_models.internet_package import InternetPackagesResponseModel
from response_models.internet_package import InternetPackageAccessTokenModel
from utils.permission_checker import PermissionChecker
from bson import ObjectId

internet_package = APIRouter()
permission_access_checker = PermissionChecker()


@internet_package.post("/v1/internet-packages/add", status_code=201, tags=['Internet Packages'],
                       summary="Add Internet Package", description="Add an Internet Package",
                       response_model=InternetPackagesResponseAdd)
async def add_internet_package(
        device_token: Annotated[str, Form()],
        source_ip: Annotated[str, Form()],
        destination_ip: Annotated[str, Form()],
        source_mac_address: Annotated[str, Form()],
        destination_mac_address: Annotated[str, Form()],
        header_type: Annotated[str, Form()],
        raw_header: Annotated[str, Form()],
        raw_payload: Annotated[str, Form()],
        authorization: Optional[str] = Header(None),
        api_key: Optional[str] = Form(None),
        secret_key: Optional[str] = Form(None),
):
    if (api_key is None and secret_key is None) and authorization is None:
        return InternetPackagesResponseAdd(success=False, message="unauthorized", internet_package=None)

    if authorization is not None:
        if not utils.users_auth.check_login_token(authorization):
            return InternetPackagesResponseAdd(success=False, message="unauthorized", internet_package=None)

    if api_key is not None and secret_key is not None:
        if not permission_access_checker.check_model_permission(AccessModelsEnum.InternetPackagesModel, api_key,
                                                                secret_key):
            return InternetPackagesResponseAdd(success=False, message="unauthorized", internet_package=None)

    if not api_key is None and not secret_key is None:
        current_access_token = DatabaseConnection.get_access_tokens_collection().find_one(
            {"api_key": api_key, "secret_key": secret_key})
    else:
        current_access_token = DatabaseConnection.get_access_tokens_collection().find_one({}, sort=[("_id", -1)])

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

    single_post_response = InternetPackagesResponseModel(
        id=internet_package_details_db[0]["id"],
        device_token=internet_package_details_db[0]["device_token"],
        source_ip=internet_package_details_db[0]["source_ip"],
        destination_ip=internet_package_details_db[0]["destination_ip"],
        source_mac_address=internet_package_details_db[0]["source_mac_address"],
        destination_mac_address=internet_package_details_db[0]["destination_mac_address"],
        header_type=internet_package_details_db[0]["header_type"],
        raw_header=internet_package_details_db[0]["raw_header"],
        raw_payload=internet_package_details_db[0]["raw_payload"],
        created_at=internet_package_details_db[0]["created_at"],
        access_token_id=internet_package_details_db[0]["access_token_id"],
        access_token_details=InternetPackageAccessTokenModel(
            issuer=current_access_token['issuer'],
            purpose=current_access_token['purpose'],
            disabled=current_access_token['disabled'],
            api_key=current_access_token['api_key'],
            secret_key=current_access_token['secret_key'],
            active_until=current_access_token['active_until'],
            access_models=current_access_token['access_models'],
            created_at=current_access_token['created_at']
        )
    )

    return InternetPackagesResponseAdd(success=True, message=None, internet_package=single_post_response)


@internet_package.get("/v1/internet-packages/", status_code=200, tags=['Internet Packages'],
                      summary="Get All Internet Packages", description="Get All Internet Packages",
                      response_model=InternetPackagesResponseIndex)
async def get_all_internet_packages(
        page: int = Query(..., description="Page number starting from 1"),
        limit: int = Query(..., description="Number of items per page"),
):
    internet_packages_details_db = all_internet_packages_serializer(
        DatabaseConnection.get_internet_packages_collection().find({}).sort("created_at", -1))

    if limit == -1:
        internet_packages_formatted = internet_packages_details_db
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        internet_packages_formatted = internet_packages_details_db[start_idx:end_idx]

    internet_packages_to_return = []
    for internet_package in internet_packages_formatted:
        access_token_details = DatabaseConnection.get_access_tokens_collection().find_one(
            {"_id": ObjectId(internet_package["access_token_id"])})
        single_post_response = InternetPackagesResponseModel(
            id=internet_package["id"],
            device_token=internet_package["device_token"],
            source_ip=internet_package["source_ip"],
            destination_ip=internet_package["destination_ip"],
            source_mac_address=internet_package["source_mac_address"],
            destination_mac_address=internet_package["destination_mac_address"],
            header_type=internet_package["header_type"],
            raw_header=internet_package["raw_header"],
            raw_payload=internet_package["raw_payload"],
            created_at=internet_package["created_at"],
            access_token_id=internet_package["access_token_id"],
            access_token_details=InternetPackageAccessTokenModel(
                issuer=access_token_details['issuer'],
                purpose=access_token_details['purpose'],
                disabled=access_token_details['disabled'],
                api_key=access_token_details['api_key'],
                secret_key=access_token_details['secret_key'],
                active_until=access_token_details['active_until'],
                access_models=access_token_details['access_models'],
                created_at=access_token_details['created_at']
            )
        )
        internet_packages_to_return.append(single_post_response)

    return InternetPackagesResponseIndex(
        success=True,
        message=None,
        current_page=page,
        current_results=len(internet_packages_to_return),
        total_results=len(internet_packages_details_db),
        all_internet_packages=list(internet_packages_to_return)
    )


@internet_package.get("/v1/internet-packages/{internet_package_id}", status_code=200, tags=['Internet Packages'],
                      summary="Get Specific Internet Package", description="Get Specific Internet Package - By ID",
                      response_model=InternetPackagesResponseView)
async def get_specific_internet_package(
        internet_package_id,
):
    try:
        internet_packages_details_db = all_internet_packages_serializer(
            DatabaseConnection.get_internet_packages_collection().find({"_id": ObjectId(internet_package_id)}))

        if internet_packages_details_db is None:
            return InternetPackagesResponseView(success=False, message="Internet Package does NOT exists",
                                                internet_package=None)

        access_token_details = DatabaseConnection.get_access_tokens_collection().find_one(
            {"_id": ObjectId(internet_packages_details_db[0]["access_token_id"])})
        single_internet_package_response = InternetPackagesResponseModel(
            id=internet_packages_details_db[0]["id"],
            device_token=internet_packages_details_db[0]["device_token"],
            source_ip=internet_packages_details_db[0]["source_ip"],
            destination_ip=internet_packages_details_db[0]["destination_ip"],
            source_mac_address=internet_packages_details_db[0]["source_mac_address"],
            destination_mac_address=internet_packages_details_db[0]["destination_mac_address"],
            header_type=internet_packages_details_db[0]["header_type"],
            raw_header=internet_packages_details_db[0]["raw_header"],
            raw_payload=internet_packages_details_db[0]["raw_payload"],
            created_at=internet_packages_details_db[0]["created_at"],
            access_token_id=internet_packages_details_db[0]["access_token_id"],
            access_token_details=InternetPackageAccessTokenModel(
                issuer=access_token_details['issuer'],
                purpose=access_token_details['purpose'],
                disabled=access_token_details['disabled'],
                api_key=access_token_details['api_key'],
                secret_key=access_token_details['secret_key'],
                active_until=access_token_details['active_until'],
                access_models=access_token_details['access_models'],
                created_at=access_token_details['created_at']
            )
        )

        return InternetPackagesResponseView(success=True, message=None,
                                            internet_package=single_internet_package_response)
    except Exception as ex:
        return InternetPackagesResponseView(success=False, message="Internet Package does NOT exists",
                                            internet_package=None)


@internet_package.post("/v1/internet-packages/{internet_package_id}", status_code=200, tags=['Internet Packages'],
                       summary="Update Specific Internet Package",
                       description="Update Specific Internet Package - By ID",
                       response_model=InternetPackagesResponseUpdate)
async def update_specific_internet_package(
        internet_package_id,
        source_ip: Annotated[str, Form()],
        destination_id: Annotated[str, Form()],
        source_mac_address: Annotated[str, Form()],
        destination_mac_address: Annotated[str, Form()],
        header_type: Annotated[str, Form()],
        raw_header: Annotated[str, Form()],
        raw_payload: Annotated[str, Form()],
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return InternetPackagesResponseUpdate(success=False, message="unauthorized")

    try:
        internet_package_object_id = ObjectId(internet_package_id)
        existing_internet_package = DatabaseConnection.get_internet_packages_collection().find_one(
            {"_id": internet_package_object_id})

        if existing_internet_package is None:
            return InternetPackagesResponseUpdate(success=False, message="Internet Package not exists")

        existing_internet_package['source_ip'] = source_ip
        existing_internet_package['destination_id'] = destination_id
        existing_internet_package['source_mac_address'] = source_mac_address
        existing_internet_package['destination_mac_address'] = destination_mac_address
        existing_internet_package['header_type'] = header_type
        existing_internet_package['raw_header'] = raw_header
        existing_internet_package['raw_payload'] = raw_payload

        DatabaseConnection.get_internet_packages_collection().update_one({"_id": internet_package_object_id},
                                                                         {"$set": existing_internet_package})

        return InternetPackagesResponseUpdate(success=True, message="Internet Package Updated Successfully")
    except Exception as ex:
        return InternetPackagesResponseUpdate(success=False,
                                              message="There was an error during internet package update")


@internet_package.delete("/v1/internet-packages/{internet_package_id}", status_code=200, tags=['Internet Packages'],
                         summary="Delete Specific Internet Package",
                         description="Delete Specific Internet Package - By ID",
                         response_model=InternetPackagesResponseDelete)
async def delete_specific_internet_package(
        internet_package_id,
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return InternetPackagesResponseDelete(success=False, message="unauthorized")

    try:
        internet_package_object_id = ObjectId(internet_package_id)
        DatabaseConnection.get_internet_packages_collection().delete_one({"_id": internet_package_object_id})

        return InternetPackagesResponseDelete(success=True, message="Internet Package Deleted Successfully")
    except Exception as ex:
        return InternetPackagesResponseDelete(success=False,
                                              message="There was an error during internet package deletion")
