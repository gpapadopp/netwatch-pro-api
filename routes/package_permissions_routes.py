from bson import ObjectId
from fastapi import APIRouter, Form, Query, Header
from typing import Optional, Annotated
from models.package_permissions_model import PackagePermissions
from schemas.package_permissions_schema import all_package_permissions_serializer
from config.db import DatabaseConnection
from utils.all_permissions import AllAppPermissions
import utils.package_permission_prediction_enum
from utils.permission_checker import PermissionChecker
from enums.access_models_enum import AccessModelsEnum
import tensorflow as tf
import os
import utils.users_auth
from response_models.package_permission import PackagePermissionsResponseModel
from response_models.package_permission import PackagePermissionsAccessTokenModel
from enums.permissions_danger.minimal_risk_enum import MinimalRiskPermissionsEnum
from enums.permissions_danger.low_risk_enum import LowRiskPermissionsEnum
from enums.permissions_danger.moderate_risk_enum import ModerateRiskPermissionsEnum
from enums.permissions_danger.high_risk_enum import HighRiskPermissionsEnum
from enums.permissions_danger.most_dangerous_enum import MostDangerousPermissionsEnum
from responses.package_permissions_responses import PackagePermissionsResponsePredict
from responses.package_permissions_responses import PackagePermissionsResponseIndexWithPagination
from responses.package_permissions_responses import PackagePermissionsResponseView
from responses.package_permissions_responses import PackagePermissionsResponseEdit
from responses.package_permissions_responses import PackagePermissionsResponseDelete

package_permission = APIRouter()

current_script_directory = os.path.dirname(os.path.abspath(__file__))
project_base_directory = os.path.abspath(os.path.join(current_script_directory, ".."))
model_file_path = os.path.abspath(project_base_directory + "/utils/trained_models/package_permissions_model.keras")

trained_model = tf.keras.models.load_model(model_file_path)
all_permissions = AllAppPermissions()
permission_access_checker = PermissionChecker()


@package_permission.post("/v1/package-permissions/predict", status_code=201, tags=["Package Permissions"], summary="Predict Benign/Malware on Permissions", description="Predict Benign/Malware based on Permissions sent by user", response_model=PackagePermissionsResponsePredict)
async def add_package_permission(
    device_token: Optional[str] = Form(None),
    package_name: Optional[str] = Form(None),
    app_name: Optional[str] = Form(None),
    permissions: Optional[str] = Form(None),
    certificate_subjects: Optional[str] = Form(None),
    certificate_issuers: Optional[str] = Form(None),
    certificate_serial_numbers: Optional[str] = Form(None),
    certificate_versions: Optional[str] = Form(None),
    api_key: Optional[str] = Form(None),
    secret_key: Optional[str] = Form(None),
):
    if api_key is None or secret_key is None:
        return PackagePermissionsResponsePredict(success=False, message='unauthorized', is_malware=None, package_prediction=None, package_permission=None, minimal_risk_permissions=None, low_risk_permissions=None, moderate_risk_permissions=None, high_risk_permissions=None, most_dangerous_permissions=None)

    if not permission_access_checker.check_model_permission(AccessModelsEnum.PackagePermissionsModel, api_key, secret_key):
        return PackagePermissionsResponsePredict(success=False, message='unauthorized', is_malware=None,
                                                 package_prediction=None, package_permission=None,
                                                 minimal_risk_permissions=None, low_risk_permissions=None,
                                                 moderate_risk_permissions=None, high_risk_permissions=None,
                                                 most_dangerous_permissions=None)

    current_access_token = DatabaseConnection.get_access_tokens_collection().find_one({"api_key": api_key, "secret_key": secret_key})

    all_permissions.format_data_array(list(str(permissions).split(",")))
    input_features = tf.constant([all_permissions.train_data], dtype=tf.int32)
    prediction = trained_model.predict(input_features)

    threshold = 0.5
    predicted_class = (prediction >= threshold).astype(int)
    predicted_model_enum = utils.package_permission_prediction_enum.PackagePermissionPredictionEnum(predicted_class).name
    is_package_malware = "1" if predicted_model_enum is utils.package_permission_prediction_enum.PackagePermissionPredictionEnum.MALWARE else "0"

    package_permission_model = PackagePermissions(
        device_token=device_token,
        package_name=package_name,
        app_name=app_name,
        permissions=list(str(permissions).split(",")),
        certificate_subjects=list(str(certificate_subjects).split(",")),
        certificate_issuers=list(str(certificate_issuers).split(",")),
        certificate_serial_numbers=list(str(certificate_serial_numbers).split(",")),
        certificate_versions=list(str(certificate_versions).split(",")),
        is_malware=is_package_malware,
        access_token_id=str(current_access_token['_id'])
    )
    _id = DatabaseConnection.get_package_permissions_collection().insert_one(dict(package_permission_model))
    package_permission_details = all_package_permissions_serializer(
        DatabaseConnection.get_package_permissions_collection().find({"_id": _id.inserted_id}))

    permissions_request = list(str(permissions).split(","))

    minimal_risk_permissions = []
    low_risk_permissions = []
    moderate_risk_permissions = []
    high_risk_permissions = []
    most_dangerous_permissions = []

    for permission in permissions_request:
        permission_name = list(permission.split("."))[-1]
        for minimal_risk_permission in MinimalRiskPermissionsEnum:
            if minimal_risk_permission.value == permission_name:
                minimal_risk_permissions.append(permission_name)

        for low_risk_permission in LowRiskPermissionsEnum:
            if low_risk_permission.value == permission_name:
                low_risk_permissions.append(permission_name)

        for moderate_risk_permission in ModerateRiskPermissionsEnum:
            if moderate_risk_permission.value == permission_name:
                moderate_risk_permissions.append(permission_name)

        for high_risk_permission in HighRiskPermissionsEnum:
            if high_risk_permission.value == permission_name:
               high_risk_permissions.append(permission_name)

        for most_dangerous_permission in MostDangerousPermissionsEnum:
            if most_dangerous_permission.value == permission_name:
                most_dangerous_permissions.append(permission_name)

    return PackagePermissionsResponsePredict(success=True, message=None, is_malware=is_package_malware == "1",
                                             package_prediction=predicted_model_enum, package_permission=package_permission_details[0],
                                             minimal_risk_permissions=minimal_risk_permissions, low_risk_permissions=low_risk_permissions,
                                             moderate_risk_permissions=moderate_risk_permissions, high_risk_permissions=high_risk_permissions,
                                             most_dangerous_permissions=most_dangerous_permissions)


@package_permission.get("/v1/package-permissions/", status_code=200, tags=['Package Permissions'], summary="Get All Package Permissions",
                 description="Get All Package Permissions", response_model=PackagePermissionsResponseIndexWithPagination)
async def get_all_package_permissions(
        page: int = Query(..., description="Page number starting from 1"),
        limit: int = Query(..., description="Number of items per page"),
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return PackagePermissionsResponseIndexWithPagination(success=False, message="unauthorized", current_page=0, current_results=0, total_results=0, all_package_permissions=None)

    package_permissions_details_db = all_package_permissions_serializer(
        DatabaseConnection.get_package_permissions_collection().find({}).sort("created_at", -1))

    if limit == -1:
        package_permissions_formatted = package_permissions_details_db
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        package_permissions_formatted = package_permissions_details_db[start_idx:end_idx]

    package_permissions_to_return = []
    for package_apks in package_permissions_formatted:
        post_user_details = DatabaseConnection.get_access_tokens_collection().find_one(
            {"_id": ObjectId(package_apks["access_token_id"])})
        single_post_response = PackagePermissionsResponseModel(
            id=package_apks["id"],
            device_token=package_apks["device_token"],
            package_name=package_apks["package_name"],
            app_name=package_apks["app_name"],
            permissions=package_apks["permissions"],
            certificate_subjects=package_apks["certificate_subjects"],
            certificate_issuers=package_apks["certificate_issuers"],
            certificate_serial_numbers=package_apks["certificate_serial_numbers"],
            certificate_versions=package_apks["certificate_versions"],
            is_malware=package_apks["is_malware"],
            created_at=package_apks["created_at"],
            access_token_id=package_apks["access_token_id"],
            access_token_details=PackagePermissionsAccessTokenModel(
                issuer=post_user_details["issuer"],
                purpose=post_user_details["purpose"],
                disabled=post_user_details["disabled"],
                api_key=post_user_details["api_key"],
                secret_key=post_user_details["secret_key"],
                active_until=post_user_details["active_until"],
                access_models=post_user_details["access_models"],
                created_at=post_user_details["created_at"]
            )
        )
        package_permissions_to_return.append(single_post_response)

    return PackagePermissionsResponseIndexWithPagination(
        success=True,
        message=None,
        current_page=page,
        current_results=len(package_permissions_to_return),
        total_results=len(package_permissions_details_db),
        all_package_permissions=list(package_permissions_to_return)
    )


@package_permission.get("/v1/package-permissions/{package_permission_id}", status_code=200, tags=['Package Permissions'],
                 summary="Get Specific Package Permissions", description="Get Specific Package Permission - By ID",
                 response_model=PackagePermissionsResponseView)
async def get_specific_package_permission(
        package_permission_id,
        authorization: str = Header(..., description="Bearer Token")
):
    try:
        if not utils.users_auth.check_login_token(authorization):
            return PackagePermissionsResponseView(success=False, message="unauthorized", package_permissions=None)

        package_package_details_db = all_package_permissions_serializer(
            DatabaseConnection.get_package_permissions_collection().find({"_id": ObjectId(package_permission_id)}))

        if package_package_details_db is None:
            return PackagePermissionsResponseView(success=False, message="Package Permissions does NOT exists", package_permissions=None)

        post_user_details = DatabaseConnection.get_access_tokens_collection().find_one(
            {"_id": ObjectId(package_package_details_db[0]["access_token_id"])})
        single_post_response = PackagePermissionsResponseModel(
            id=package_package_details_db[0]["id"],
            device_token=package_package_details_db[0]["device_token"],
            package_name=package_package_details_db[0]["package_name"],
            app_name=package_package_details_db[0]["app_name"],
            permissions=package_package_details_db[0]["permissions"],
            certificate_subjects=package_package_details_db[0]["certificate_subjects"],
            certificate_issuers=package_package_details_db[0]["certificate_issuers"],
            certificate_serial_numbers=package_package_details_db[0]["certificate_serial_numbers"],
            certificate_versions=package_package_details_db[0]["certificate_versions"],
            is_malware=package_package_details_db[0]["is_malware"],
            created_at=package_package_details_db[0]["created_at"],
            access_token_id=package_package_details_db[0]["access_token_id"],
            access_token_details=PackagePermissionsAccessTokenModel(
                issuer=post_user_details["issuer"],
                purpose=post_user_details["purpose"],
                disabled=post_user_details["disabled"],
                api_key=post_user_details["api_key"],
                secret_key=post_user_details["secret_key"],
                active_until=post_user_details["active_until"],
                access_models=post_user_details["access_models"],
                created_at=post_user_details["created_at"]
            )
        )

        return PackagePermissionsResponseView(success=True, message=None, package_permissions=single_post_response)
    except Exception as ex:
        return PackagePermissionsResponseView(success=False, message="Package Permissions does NOT exists", package_permissions=None)


@package_permission.post("/v1/package-permissions/{package_permission_id}", status_code=200, tags=['Package Permissions'],
                  summary="Update Specific Package Permissions", description="Update Specific Package Permission - By ID",
                  response_model=PackagePermissionsResponseEdit)
async def update_specific_package_permission(
        package_permission_id,
        device_token: Annotated[str, Form()],
        package_name: Annotated[str, Form()],
        app_name: Annotated[str, Form()],
        is_malware: Annotated[str, Form()],
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return PackagePermissionsResponseEdit(success=False, message="unauthorized")

    try:
        package_permission_object_id = ObjectId(package_permission_id)
        existing_package_permission = DatabaseConnection.get_package_permissions_collection().find_one({"_id": package_permission_object_id})

        if existing_package_permission is None:
            return PackagePermissionsResponseEdit(success=False, message="Package Permission not exists")

        existing_package_permission['device_token'] = device_token
        existing_package_permission['package_name'] = package_name
        existing_package_permission['app_name'] = app_name
        existing_package_permission['is_malware'] = is_malware

        DatabaseConnection.get_package_permissions_collection().update_one({"_id": package_permission_object_id},
                                                                    {"$set": existing_package_permission})

        return PackagePermissionsResponseEdit(success=True, message="Package Permissions Updated Successfully")
    except Exception as ex:
        return PackagePermissionsResponseEdit(success=False, message="There was an error during package permissions update")


@package_permission.delete("/v1/package-permissions/{package_permission_id}", status_code=200, tags=['Package Permissions'],
                    summary="Delete Specific Package Permissions", description="Delete Specific Package Permission - By ID",
                    response_model=PackagePermissionsResponseDelete)
async def delete_specific_package_permission(
        package_permission_id,
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return PackagePermissionsResponseDelete(success=False, message="unauthorized")

    try:
        package_permissions_object_id = ObjectId(package_permission_id)
        DatabaseConnection.get_package_permissions_collection().delete_one({"_id": package_permissions_object_id})

        return PackagePermissionsResponseDelete(success=True, message="Package Permission Deleted Successfully")
    except Exception as ex:
        return PackagePermissionsResponseDelete(success=False, message="There was an error during package permission deletion")
