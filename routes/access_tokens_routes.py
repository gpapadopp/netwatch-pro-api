from fastapi import APIRouter, Form, Header, Query
from typing import Annotated
from models.access_tokens_model import AccessTokensModel
from datetime import datetime
from utils.date_time_utils import DateTimeUtils
from schemas.access_tokens_schema import all_access_tokens_serializer
from config.db import DatabaseConnection
from enums.access_models_enum import AccessModelsEnum
from utils.permission_checker import PermissionChecker
import utils.users_auth
import uuid
from bson import ObjectId
from responses.access_tokens_responses import AccessTokenResponseDelete
from responses.access_tokens_responses import AccessTokensResponseAdd
from responses.access_tokens_responses import AccessTokensResponseIndex
from responses.access_tokens_responses import AccessTokensResponseView
from responses.access_tokens_responses import AccessTokenResponseUpdate

access_token_api = APIRouter()
date_time_util_instance = DateTimeUtils()
permission_checker = PermissionChecker()


@access_token_api.post("/v1/access-tokens/add", status_code=201, tags=['Access Tokens'], summary="Add Access Token", description="Endpoint to add a new access token for public users", response_model=AccessTokensResponseAdd)
async def add_access_token(
        issuer: Annotated[str, Form()],
        purpose: Annotated[str, Form()],
        access_models: Annotated[str, Form()],
):
    access_model_split_list = access_models.split(",")
    access_models = []
    for access_model in access_model_split_list:
        access_models.append(AccessModelsEnum[access_model].value)

    generated_api_key = str(uuid.uuid4())
    generated_secret_key = str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4()) + str(uuid.uuid4())

    access_token_model = AccessTokensModel(
        issuer=issuer,
        purpose=purpose,
        disabled=False,
        api_key=generated_api_key,
        secret_key=generated_secret_key,
        active_until=date_time_util_instance.add_years(datetime.now(), 1),
        access_models=access_models
    )

    _id = DatabaseConnection.get_access_tokens_collection().insert_one(dict(access_token_model))
    access_token_details_db = all_access_tokens_serializer(
        DatabaseConnection.get_access_tokens_collection().find({"_id": _id.inserted_id}))

    return AccessTokensResponseAdd(success=True, message=None, access_token=access_token_details_db)


@access_token_api.get("/v1/access-tokens/", status_code=200, tags=['Access Tokens'], summary="Get Access Tokens", description="Endpoint to get all access tokens", response_model=AccessTokensResponseIndex)
async def get_all_access_token(
    page: int = Query(..., description="Page number starting from 0"),
    limit: int = Query(..., description="Number of items per page"),
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return AccessTokensResponseIndex(success=False, message="unauthorized", current_page=0, current_results=0, total_results=0, all_access_tokens=None)

    access_tokens_db = all_access_tokens_serializer(DatabaseConnection.get_access_tokens_collection().find({}))
    if limit == -1:
        return AccessTokensResponseIndex(success=True, message=None, current_page=1, current_results=len(access_tokens_db),
                                         total_results=len(access_tokens_db), all_access_tokens=access_tokens_db)
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        access_tokens_to_return = access_tokens_db[start_idx:end_idx]
        return AccessTokensResponseIndex(success=True, message=None, current_page=page,
                                         current_results=len(access_tokens_to_return),
                                         total_results=len(access_tokens_db), all_access_tokens=access_tokens_to_return)


@access_token_api.get("/v1/access-tokens/{access_token_id}", status_code=200, tags=['Access Tokens'], summary="Get Specific Access Token", description="Get Specific Access Token - By ID", response_model=AccessTokensResponseView)
async def get_specific_access_token(
    access_token_id,
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return AccessTokensResponseView(success=False, message='unauthorized', access_token_details=None)

    try:
        access_token_details_db = all_access_tokens_serializer(
            DatabaseConnection.get_access_tokens_collection().find({"_id": ObjectId(access_token_id)}))

        if access_token_details_db is None:
            return AccessTokensResponseView(success=False, message='Access token does NOT exists', access_token_details=None)

        return AccessTokensResponseView(success=True, message=None, access_token_details=access_token_details_db[0])
    except Exception as e:
        return AccessTokensResponseView(success=False, message='Access token does NOT exists',
                                        access_token_details=None)


@access_token_api.post("/v1/access-tokens/{access_token_id}", status_code=200, tags=['Access Tokens'], summary="Update Specific Access Token", description="Update Specific Access Token - By ID", response_model=AccessTokenResponseUpdate)
async def update_specific_access_token(
    access_token_id,
    issuer: Annotated[str, Form()],
    purpose: Annotated[str, Form()],
    disabled: Annotated[bool, Form()],
    access_models: Annotated[str, Form()],
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return AccessTokenResponseUpdate(success=False, message="unauthorized")

    try:
        access_token_object_id = ObjectId(access_token_id)
        existing_access_token = DatabaseConnection.get_access_tokens_collection().find_one({"_id": access_token_object_id})

        if existing_access_token is None:
            return AccessTokenResponseUpdate(success=False, message="Access token does NOT exists")

        existing_access_token['issuer'] = issuer
        existing_access_token['purpose'] = purpose
        existing_access_token['disabled'] = disabled
        access_model_split_list = access_models.split(",")
        access_models = []
        for access_model in access_model_split_list:
            access_models.append(AccessModelsEnum[access_model].value)

        existing_access_token['access_models'] = access_models

        DatabaseConnection.get_access_tokens_collection().update_one({"_id": access_token_object_id}, {"$set": existing_access_token})

        return AccessTokenResponseUpdate(success=True, message="Access Token Updated Successfully")
    except Exception as ex:
        return AccessTokenResponseUpdate(success=False, message="Access token does NOT exists")


@access_token_api.delete("/v1/access-tokens/{access_token_id}", status_code=200, tags=['Access Tokens'], summary="Delete Specific Access Token", description="Delete Specific Access Token - By ID", response_model=AccessTokenResponseDelete)
async def delete_specific_access_token(
    access_token_id,
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return AccessTokenResponseDelete(success=False, message='unauthorized')

    try:
        access_token_object_id = ObjectId(access_token_id)
        existing_access_token = DatabaseConnection.get_access_tokens_collection().find_one({"_id": access_token_object_id})

        if existing_access_token is None:
            return AccessTokenResponseDelete(success=False, message='Access token does NOT exists')

        DatabaseConnection.get_access_tokens_collection().delete_one({"_id": access_token_object_id})

        return AccessTokenResponseDelete(success=True, message='Access Token Deleted Successfully')
    except Exception as ex:
        return AccessTokenResponseDelete(success=False, message='Access token does NOT exists')
