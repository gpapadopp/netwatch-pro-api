from fastapi import APIRouter, UploadFile, File, Form
from typing import Annotated
from models.package_apks_model import PackageApks
from schemas.package_apks_schema import all_package_apks_serializer, package_apks_serializer
from config.db import package_apks_collection
import uuid
import hashlib
import os

package_apk = APIRouter()


@package_apk.post("/v1/package-apks/predict", status_code=201)
async def predict_package_apks(
        device_token: Annotated[str, Form()],
        package_name: Annotated[str, Form()],
        app_name: Annotated[str, Form()],
        apk_file: UploadFile = File(...)
):
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

    package_apk_model = PackageApks(
        device_token=device_token,
        package_name=package_name,
        app_name=app_name,
        apk_file=file_unique_name,
        md5_checksum=uploaded_apk_md5
    )

    _id = package_apks_collection.insert_one(dict(package_apk_model))
    package_apk_details_db = all_package_apks_serializer(
        package_apks_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "is_malware": None,
        "package_apk": package_apk_details_db
    }
