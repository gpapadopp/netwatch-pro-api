from fastapi import APIRouter, Form
from typing import Optional
from models.package_permissions_model import PackagePermissions
from schemas.package_permissions_schema import all_package_permissions_serializer
from config.db import package_permissions_collection
from config.db import access_tokens_collection
from utils.all_permissions import AllAppPermissions
import utils.package_permission_prediction_enum
from utils.permission_checker import PermissionChecker
from enums.access_models_enum import AccessModelsEnum
import tensorflow as tf
import os
from enums.permissions_danger.minimal_risk_enum import MinimalRiskPermissionsEnum
from enums.permissions_danger.low_risk_enum import LowRiskPermissionsEnum
from enums.permissions_danger.moderate_risk_enum import ModerateRiskPermissionsEnum
from enums.permissions_danger.high_risk_enum import HighRiskPermissionsEnum
from enums.permissions_danger.most_dangerous_enum import MostDangerousPermissionsEnum
from responses.package_permissions_responses import PackagePermissionsResponsePredict

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

    current_access_token = access_tokens_collection.find_one({"api_key": api_key, "secret_key": secret_key})

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
    _id = package_permissions_collection.insert_one(dict(package_permission_model))
    package_permission_details = all_package_permissions_serializer(
        package_permissions_collection.find({"_id": _id.inserted_id}))

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
