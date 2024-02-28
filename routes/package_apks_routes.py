from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated, Optional
from models.package_apks_model import PackageApks
from schemas.package_apks_schema import all_package_apks_serializer, package_apks_serializer
from config.db import package_apks_collection
import uuid
import hashlib
import os
import tensorflow as tf
from utils.permission_checker import PermissionChecker
from enums.access_models_enum import AccessModelsEnum
from utils.package_apk_analyzer.analyze_apks import AnalyzeApks
import utils.package_apk_prediction_enum
from responses.package_apks_responses import PackageApksResponsePredict

package_apk = APIRouter()

current_script_directory = os.path.dirname(os.path.abspath(__file__))
project_base_directory = os.path.abspath(os.path.join(current_script_directory, ".."))
model_file_path = os.path.abspath(project_base_directory + "/utils/trained_models/package_apks_model.keras")

trained_model = tf.keras.models.load_model(model_file_path)
permission_access_checker = PermissionChecker()
package_analyzer = AnalyzeApks()


@package_apk.post("/v1/package-apks/predict", status_code=201, tags=['Package APKs'], summary="Predict Benign/Malware on APKs", description="Predict Benign/Malware on Uploaded APK File", response_model=PackageApksResponsePredict)
async def predict_package_apks(
        device_token: Annotated[str, Form()],
        package_name: Annotated[str, Form()],
        app_name: Annotated[str, Form()],
        api_key: Optional[str] = Form(None),
        secret_key: Optional[str] = Form(None),
        apk_file: UploadFile = File(...)
):
    if api_key is None or secret_key is None:
        return {
            "status": "error",
            "message": "unauthorized"
        }

    if not permission_access_checker.check_model_permission(AccessModelsEnum.PackageAPKsModel, api_key, secret_key):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    unique_filename = str(uuid.uuid4())
    apk_file_extension = apk_file.filename.split(".")[1]
    file_unique_name = unique_filename + "." + apk_file_extension
    file_location = f"files/apk_files/{file_unique_name}"
    with open(file_location, "wb+") as file_object:
        file_object.write(apk_file.file.read())

    md5 = hashlib.md5()
    with open(file_location, 'rb') as file:
        # Read the file in chunks of 4096 bytes at a time
        for chunk in iter(lambda: file.read(4096), b''):
            md5.update(chunk)

    uploaded_apk_md5 = md5.hexdigest()

    # Check MD5 Exists in DB
    apk_db = package_apks_collection.find_one({"md5_checksum": uploaded_apk_md5})
    if apk_db:
        os.remove(file_location)
        return {
            "status": "success",
            "is_malware": None if (apk_db['is_malware'] is None or apk_db['is_malware'] == 'None') else bool(apk_db['is_malware']),
            "apk_package_details": package_apks_serializer(apk_db)
        }

    # Make Prediction with Model
    package_analyzer.initialize_variables(file_location)
    package_analyzer.extract_apk_info()
    input_features = tf.constant([package_analyzer.format_data()], dtype=tf.int32)
    prediction = trained_model.predict(input_features)

    threshold = 0.5
    predicted_class = (prediction >= threshold).astype(int)
    predicted_model_enum = utils.package_apk_prediction_enum.PackageApkPredictionEnum(
        predicted_class).name
    is_package_malware = "1" if predicted_model_enum is utils.package_apk_prediction_enum.PackageApkPredictionEnum.MALWARE else "0"

    package_apk_model = PackageApks(
        device_token=device_token,
        package_name=package_name,
        app_name=app_name,
        apk_file=file_unique_name,
        md5_checksum=uploaded_apk_md5,
        is_malware=is_package_malware
    )

    _id = package_apks_collection.insert_one(dict(package_apk_model))
    package_apk_details_db = all_package_apks_serializer(
        package_apks_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "is_malware": is_package_malware,
        "package_apk": package_apk_details_db
    }
