from fastapi import APIRouter, UploadFile, File, Form, Header, Query
from typing import Annotated
from models.malicious_files_signatures import MaliciousFilesSignatures
from schemas.malicious_files_signatures_schema import all_malicious_files_signatures_serializer
from config.db import DatabaseConnection
import utils.users_auth
import uuid
import csv
from bson import ObjectId
from response_models.malicious_files_signatures import MaliciousFilesSignaturesResponseModel
from responses.malicious_files_signatures_responses import MaliciousFilesSignaturesResponseIndexWithPagination
from responses.malicious_files_signatures_responses import MaliciousFilesSignaturesResponseAdd
from responses.malicious_files_signatures_responses import MaliciousFilesSignaturesResponseView
from responses.malicious_files_signatures_responses import MaliciousFilesSignaturesResponseEdit
from responses.malicious_files_signatures_responses import MaliciousFilesSignaturesResponseDelete

malicious_files_signatures_api = APIRouter()


@malicious_files_signatures_api.post("/v1/malicious-files-signatures/add", status_code=201,
                                     tags=['Malicious Files Signatures'], summary="Add a Malicious File Signature",
                                     description="Add a New Malicious File Signature",
                                     response_model=MaliciousFilesSignaturesResponseAdd)
async def add_malicious_file_signature(
        file_signature: Annotated[str, Form()],
        file_signature_type: Annotated[str, Form()],
        file_category: Annotated[str, Form()],
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return MaliciousFilesSignaturesResponseAdd(success=False, message="unauthorized", malicious_file_signature=None)

    same_signature_file = DatabaseConnection.get_malicious_files_signatures_collection().find_one(
        {"file_signature": file_signature})
    if same_signature_file:
        return MaliciousFilesSignaturesResponseAdd(success=False, message="Malicious File Signature Already Exists",
                                                   malicious_file_signature=None)

    malicious_file_signature_model = MaliciousFilesSignatures(
        file_signature=file_signature,
        file_signature_type=file_signature_type,
        file_category=file_category
    )

    _id = DatabaseConnection.get_malicious_files_signatures_collection().insert_one(
        dict(malicious_file_signature_model))
    malicious_file_signature_details_db = all_malicious_files_signatures_serializer(
        DatabaseConnection.get_malicious_files_signatures_collection().find({"_id": _id.inserted_id}))

    malicious_file_to_return = MaliciousFilesSignaturesResponseModel(
        id=malicious_file_signature_details_db[0]['id'],
        file_signature=malicious_file_signature_details_db[0]["file_signature"],
        file_signature_type=malicious_file_signature_details_db[0]["file_signature_type"],
        file_category=malicious_file_signature_details_db[0]["file_category"],
        created_at=malicious_file_signature_details_db[0]["created_at"]
    )

    return MaliciousFilesSignaturesResponseAdd(success=True, message=None,
                                               malicious_file_signature=malicious_file_to_return)


@malicious_files_signatures_api.post("/v1/malicious-files-signatures/add-csv", status_code=201,
                                     tags=['Malicious Files Signatures'],
                                     summary="Add a Malicious File Signature - CSV",
                                     description="Add a New Malicious File Signature using a CSV File",
                                     response_model=MaliciousFilesSignaturesResponseAdd)
async def add_malicious_file_signature_csv(
        csv_file: UploadFile = File(...),
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return MaliciousFilesSignaturesResponseAdd(success=False, message="unauthorized", notification=None)

    unique_filename = str(uuid.uuid4())
    banner_extension = csv_file.filename.split(".")[1]
    file_unique_name = unique_filename + "." + banner_extension
    file_location = f"files/malicious_file_signatures/{file_unique_name}"
    with open(file_location, "wb+") as file_object:
        file_object.write(csv_file.file.read())

    csv_file_opened = open(file_location)
    csv_reader = csv.reader(csv_file_opened)
    for row in csv_reader:
        md5_checksum = row[0]
        md5_type = row[1]
        same_signature_file = DatabaseConnection.get_malicious_files_signatures_collection().find_one(
            {"file_signature": md5_checksum})
        if same_signature_file:
            continue
        else:
            malicious_file_signature_model = MaliciousFilesSignatures(
                file_signature=md5_checksum,
                file_signature_type='md5',
                file_category=md5_type
            )
            DatabaseConnection.get_malicious_files_signatures_collection().insert_one(
                dict(malicious_file_signature_model))

    return MaliciousFilesSignaturesResponseAdd(success=True, message="CSV File Imported Successfully",
                                               notification=None)


@malicious_files_signatures_api.get("/v1/malicious-files-signatures/with-pagination", status_code=200, tags=['Malicious Files Signatures'], summary="Get All Malicious Files Signatures - With Pagination",
                   description="Get All Malicious Files Signatures - With Pagination", response_model=MaliciousFilesSignaturesResponseIndexWithPagination)
async def get_all_malicious_files_signatures(
        page: int = Query(..., description="Page number starting from 1"),
        limit: int = Query(..., description="Number of items per page"),
):
    malicious_files_signatures_details_db = all_malicious_files_signatures_serializer(
        DatabaseConnection.get_malicious_files_signatures_collection().find({}).sort("created_at", -1))

    if limit == -1:
        malicious_files_formatted_formatted = malicious_files_signatures_details_db
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        malicious_files_formatted_formatted = malicious_files_signatures_details_db[start_idx:end_idx]

    malicious_files_to_return = []
    for single_file in malicious_files_formatted_formatted:
        single_post_response = MaliciousFilesSignaturesResponseModel(
            id=single_file["id"],
            file_signature=single_file["file_signature"],
            file_signature_type=single_file["file_signature_type"],
            file_category=single_file["file_category"],
            created_at=single_file["created_at"]
        )
        malicious_files_to_return.append(single_post_response)

    return MaliciousFilesSignaturesResponseIndexWithPagination(
        success=True,
        message=None,
        current_page=page,
        current_results=len(malicious_files_to_return),
        total_results=len(malicious_files_signatures_details_db),
        malicious_file_signatures=list(malicious_files_to_return)
    )


@malicious_files_signatures_api.get("/v1/malicious-files-signatures/{malicious_file_signature_id}", status_code=200, tags=['Malicious Files Signatures'],
                   summary="Get Specific Malicious File Signature", description="Get Specific Malicious File Signature - By ID",
                   response_model=MaliciousFilesSignaturesResponseView)
async def get_specific_malicious_files_signatures(
        malicious_file_signature_id,
):
    try:
        malicious_files_signatures_details_db = all_malicious_files_signatures_serializer(DatabaseConnection.get_malicious_files_signatures_collection().find({"_id": ObjectId(malicious_file_signature_id)}))

        if malicious_files_signatures_details_db is None:
            return MaliciousFilesSignaturesResponseView(success=False, message="Blog Post does NOT exists", malicious_file_signature=None)

        single_malicious_file_signature_response = MaliciousFilesSignaturesResponseModel(
            id=malicious_files_signatures_details_db[0]["id"],
            file_signature=malicious_files_signatures_details_db[0]["file_signature"],
            file_signature_type=malicious_files_signatures_details_db[0]["file_signature_type"],
            file_category=malicious_files_signatures_details_db[0]["file_category"],
            created_at=malicious_files_signatures_details_db[0]["created_at"]
        )

        return MaliciousFilesSignaturesResponseView(success=True, message=None, malicious_file_signature=single_malicious_file_signature_response)
    except Exception as ex:
        return MaliciousFilesSignaturesResponseView(success=False, message="Malicious File Signature does NOT exists", malicious_file_signature=None)


@malicious_files_signatures_api.post("/v1/malicious-files-signatures/{malicious_file_signature_id}", status_code=200, tags=['Malicious Files Signatures'], summary="Update Specific Malicious File Signatures", description="Update Specific Malicious File Signatures - By ID", response_model=MaliciousFilesSignaturesResponseEdit)
async def update_specific_malicious_file_signature(
    malicious_file_signature_id,
    file_signature: Annotated[str, Form()],
    file_signature_type: Annotated[str, Form()],
    file_category: Annotated[str, Form()],
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return MaliciousFilesSignaturesResponseEdit(success=False, message="unauthorized")

    try:
        malicious_file_signature_exists = DatabaseConnection.get_malicious_files_signatures_collection().find_one(
            {"file_signature": file_signature})
        if malicious_file_signature_exists:
            return MaliciousFilesSignaturesResponseEdit(success=False, message="Malicious File Signature already exists")

        malicious_file_signatures_object_id = ObjectId(malicious_file_signature_id)
        existing_malicious_files_signatures = DatabaseConnection.get_malicious_files_signatures_collection().find_one({"_id": malicious_file_signatures_object_id})

        if existing_malicious_files_signatures is None:
            return MaliciousFilesSignaturesResponseEdit(success=False, message="Malicious File Signature not exists")

        existing_malicious_files_signatures['file_signature'] = file_signature
        existing_malicious_files_signatures['file_signature_type'] = file_signature_type
        existing_malicious_files_signatures['file_category'] = file_category

        DatabaseConnection.get_malicious_files_signatures_collection().update_one({"_id": malicious_file_signatures_object_id}, {"$set": existing_malicious_files_signatures})

        return MaliciousFilesSignaturesResponseEdit(success=True, message="Malicious File Signature Updated Successfully")
    except Exception as ex:
        return MaliciousFilesSignaturesResponseEdit(success=False, message="There was an error during malicious file signature update")


@malicious_files_signatures_api.delete("/v1/malicious-files-signatures/{malicious_file_signature_id}", status_code=200, tags=['Malicious Files Signatures'],
                      summary="Delete Specific Malicious Files Signature", description="Delete Specific Malicious File Signature - By ID",
                      response_model=MaliciousFilesSignaturesResponseDelete)
async def delete_specific_malicious_file_signature(
        malicious_file_signature_id,
        authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return MaliciousFilesSignaturesResponseDelete(success=False, message="unauthorized")

    try:
        malicious_file_signatures_object_id = ObjectId(malicious_file_signature_id)
        DatabaseConnection.get_malicious_files_signatures_collection().delete_one({"_id": malicious_file_signatures_object_id})

        return MaliciousFilesSignaturesResponseDelete(success=True, message="Malicious File Signature Deleted Successfully")
    except Exception as ex:
        return MaliciousFilesSignaturesResponseDelete(success=False, message="There was an error during malicious file signature deletion")
