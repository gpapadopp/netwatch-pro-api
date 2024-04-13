from bson import ObjectId
from fastapi import APIRouter, UploadFile, File, Form, Query, Header
from typing import Annotated, Optional
from models.package_apks_model import PackageApks
from schemas.package_apks_schema import all_package_apks_serializer
from config.db import DatabaseConnection
import uuid
import hashlib
import os
import tensorflow as tf
import utils.users_auth
from utils.permission_checker import PermissionChecker
from enums.access_models_enum import AccessModelsEnum
from utils.package_apk_analyzer.analyze_apks import AnalyzeApks
import utils.package_apk_prediction_enum
from response_models.package_apk import PackageApkAccessTokenModel
from response_models.package_apk import PackageApksResponseModel
from responses.package_apks_responses import PackageApksResponsePredict
from responses.package_apks_responses import PackageApksResponseIndexWithPagination
from responses.package_apks_responses import PackageApksResponseView
from responses.package_apks_responses import PackageApksResponseEdit
from responses.package_apks_responses import PackageApksResponseDelete

package_apk = APIRouter()

current_script_directory = os.path.dirname(os.path.abspath(__file__))
project_base_directory = os.path.abspath(os.path.join(current_script_directory, ".."))
model_file_path = os.path.abspath(project_base_directory + "/utils/trained_models/package_apks_model.keras")

trained_model = tf.keras.models.load_model(model_file_path)
permission_access_checker = PermissionChecker()
package_analyzer = AnalyzeApks()


@package_apk.post("/v1/package-apks/predict", status_code=201, tags=['Package APKs'],
                  summary="Predict Benign/Malware on APKs", description="Predict Benign/Malware on Uploaded APK File",
                  response_model=PackageApksResponsePredict)
async def predict_package_apks(
        device_token: Annotated[str, Form()],
        package_name: Annotated[str, Form()],
        app_name: Annotated[str, Form()],
        api_key: Optional[str] = Form(None),
        secret_key: Optional[str] = Form(None),
        apk_file: UploadFile = File(...)
):
    if api_key is None or secret_key is None:
        return PackageApksResponsePredict(success=False, message="unauthorized", is_malware=None, package_apk=None)

    if not permission_access_checker.check_model_permission(AccessModelsEnum.PackageAPKsModel, api_key, secret_key):
        return PackageApksResponsePredict(success=False, message="unauthorized", is_malware=None, package_apk=None)

    current_access_token = DatabaseConnection.get_access_tokens_collection().find_one(
        {"api_key": api_key, "secret_key": secret_key})

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
    apk_db = DatabaseConnection.get_package_apks_collection().find_one({"md5_checksum": uploaded_apk_md5})
    if apk_db:
        os.remove(file_location)
        package_apk_model = PackageApks(
            device_token=str(apk_db['device_token']),
            package_name=str(apk_db['package_name']),
            app_name=str(apk_db['app_name']),
            apk_file=str(apk_db['apk_file']),
            md5_checksum=str(apk_db['md5_checksum']),
            is_malware=str(apk_db['is_malware']),
            access_token_id=str(current_access_token['_id'])
        )
        _id = DatabaseConnection.get_package_apks_collection().insert_one(dict(package_apk_model))
        package_apk_details_db = all_package_apks_serializer(
            DatabaseConnection.get_package_apks_collection().find({"_id": _id.inserted_id}))

        return PackageApksResponsePredict(success=True, message=None, is_malware=None if (
                    apk_db['is_malware'] is None or apk_db['is_malware'] == 'None') else bool(apk_db['is_malware']),
                                          package_apk=package_apk_details_db[0])

    # Make Prediction with Model
    package_analyzer.initialize_variables(file_location)
    package_analyzer.extract_apk_info()
    input_features = tf.constant(package_analyzer.format_data(), dtype=tf.int32)
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
        is_malware=is_package_malware,
        access_token_id=str(current_access_token['_id'])
    )

    _id = DatabaseConnection.get_package_apks_collection().insert_one(dict(package_apk_model))
    package_apk_details_db = all_package_apks_serializer(
        DatabaseConnection.get_package_apks_collection().find({"_id": _id.inserted_id}))

    return PackageApksResponsePredict(success=True, message=None, is_malware=is_package_malware,
                                      package_apk=package_apk_details_db[0])


@package_apk.get("/v1/package-apks/", status_code=200, tags=['Package APKs'], summary="Get All Package APKs",
                 description="Get All Package APKs", response_model=PackageApksResponseIndexWithPagination)
async def get_all_package_apks(
        page: int = Query(..., description="Page number starting from 1"),
        limit: int = Query(..., description="Number of items per page"),
):
    package_apks_details_db = all_package_apks_serializer(
        DatabaseConnection.get_package_apks_collection().find({}).sort("created_at", -1))

    if limit == -1:
        blog_posts_formatted = package_apks_details_db
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        blog_posts_formatted = package_apks_details_db[start_idx:end_idx]

    package_apks_to_return = []
    for package_apks in blog_posts_formatted:
        post_user_details = DatabaseConnection.get_access_tokens_collection().find_one(
            {"_id": ObjectId(package_apks["access_token_id"])})
        single_post_response = PackageApksResponseModel(
            id=package_apks["id"],
            device_token=package_apks["device_token"],
            package_name=package_apks["package_name"],
            app_name=package_apks["app_name"],
            apk_file=package_apks["apk_file"],
            is_malware=package_apks["is_malware"],
            created_at=package_apks["created_at"],
            md5_checksum=package_apks["md5_checksum"],
            access_token_id=package_apks["access_token_id"],
            access_token_details=PackageApkAccessTokenModel(
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
        package_apks_to_return.append(single_post_response)

    return PackageApksResponseIndexWithPagination(
        success=True,
        message=None,
        current_page=page,
        current_results=len(package_apks_to_return),
        total_results=len(package_apks_details_db),
        all_package_apks=list(package_apks_to_return)
    )


@package_apk.get("/v1/package-apks/{package_apk_id}", status_code=200, tags=['Package APKs'],
                 summary="Get Specific Package APKs", description="Get Specific Package APKs - By ID",
                 response_model=PackageApksResponseView)
async def get_specific_package_apk(
        package_apk_id,
):
    try:
        package_apk_details_db = all_package_apks_serializer(
            DatabaseConnection.get_package_apks_collection().find({"_id": ObjectId(package_apk_id)}))

        if package_apk_details_db is None:
            return PackageApksResponseView(success=False, message="Package APK does NOT exists", package_apk=None)

        post_user_details = DatabaseConnection.get_access_tokens_collection().find_one(
            {"_id": ObjectId(package_apk_details_db[0]["access_token_id"])})
        single_post_response = PackageApksResponseModel(
            id=package_apk_details_db[0]["id"],
            device_token=package_apk_details_db[0]["device_token"],
            package_name=package_apk_details_db[0]["package_name"],
            app_name=package_apk_details_db[0]["app_name"],
            apk_file=package_apk_details_db[0]["apk_file"],
            is_malware=package_apk_details_db[0]["is_malware"],
            created_at=package_apk_details_db[0]["created_at"],
            md5_checksum=package_apk_details_db[0]["md5_checksum"],
            access_token_id=package_apk_details_db[0]["access_token_id"],
            access_token_details=PackageApkAccessTokenModel(
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

        return PackageApksResponseView(success=True, message=None, package_apk=single_post_response)
    except Exception as ex:
        return PackageApksResponseView(success=False, message="Package APK does NOT exists", package_apk=None)


@package_apk.post("/v1/package-apks/{package_apk_id}", status_code=200, tags=['Package APKs'],
                  summary="Update Specific Package APK", description="Update Specific Package APK - By ID",
                  response_model=PackageApksResponseEdit)
async def update_specific_package_apk(
        package_apk_id,
        device_token: Annotated[str, Form()],
        is_malware: Annotated[str, Form()],
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return PackageApksResponseEdit(success=False, message="unauthorized")

    try:
        package_apk_object_id = ObjectId(package_apk_id)
        existing_package_apk = DatabaseConnection.get_package_apks_collection().find_one({"_id": package_apk_object_id})

        if existing_package_apk is None:
            return PackageApksResponseEdit(success=False, message="Package APK not exists")

        existing_package_apk['device_token'] = device_token
        existing_package_apk['is_malware'] = is_malware

        DatabaseConnection.get_package_apks_collection().update_one({"_id": package_apk_object_id},
                                                                    {"$set": existing_package_apk})

        return PackageApksResponseEdit(success=True, message="Package APK Updated Successfully")
    except Exception as ex:
        return PackageApksResponseEdit(success=False, message="There was an error during package apk update")


@package_apk.delete("/v1/package-apks/{package_apk_id}", status_code=200, tags=['Package APKs'],
                      summary="Delete Specific Package APK", description="Delete Specific Package APK - By ID",
                      response_model=PackageApksResponseDelete)
async def delete_specific_package_apk(
        package_apk_id,
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return PackageApksResponseDelete(success=False, message="unauthorized")

    try:
        package_apk_object_id = ObjectId(package_apk_id)
        DatabaseConnection.get_blog_posts_collection().delete_one({"_id": package_apk_object_id})

        return PackageApksResponseDelete(success=True, message="Package APK Deleted Successfully")
    except Exception as ex:
        return PackageApksResponseDelete(success=False, message="There was an error during blog post deletion")
