from fastapi import APIRouter, Form
from typing import Optional
from models.package_permissions_model import PackagePermissions
from schemas.package_permissions_schema import all_package_permissions_serializer
from config.db import package_permissions_collection
from utils.all_permissions import AllAppPermissions
import utils.package_permission_prediction_enum
from utils.permission_checker import PermissionChecker
from enums.access_models_enum import AccessModelsEnum
import tensorflow as tf
import os

package_permission = APIRouter()

current_script_directory = os.path.dirname(os.path.abspath(__file__))
project_base_directory = os.path.abspath(os.path.join(current_script_directory, ".."))
model_file_path = os.path.abspath(project_base_directory + "/utils/trained_models/package_permissions_model.keras")

trained_model = tf.keras.models.load_model(model_file_path)
all_permissions = AllAppPermissions()
permission_access_checker = PermissionChecker()


@package_permission.post("/v1/package-permissions/predict", status_code=201)
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
        return {
            "status": "error",
            "message": "unauthorized"
        }

    if not permission_access_checker.check_model_permission(AccessModelsEnum.PackagePermissionsModel, api_key, secret_key):
        return {
            "status": "error",
            "message": "unauthorized"
        }

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
        is_malware=is_package_malware
    )
    _id = package_permissions_collection.insert_one(dict(package_permission_model))
    package_permission_details = all_package_permissions_serializer(
        package_permissions_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "is_malware": is_package_malware == "1",
        "package_prediction": predicted_model_enum,
        "package_permission": package_permission_details
    }
