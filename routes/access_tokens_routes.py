from fastapi import APIRouter, Form, Header, Query
from typing import Annotated
from models.access_tokens_model import AccessTokensModel
from datetime import datetime
from utils.date_time_utils import DateTimeUtils
from schemas.access_tokens_schema import all_access_tokens_serializer
from config.db import access_tokens_collection
from enums.access_models_enum import AccessModelsEnum
from utils.permission_checker import PermissionChecker
import utils.users_auth
import uuid
from bson import ObjectId

access_token_api = APIRouter()
date_time_util_instance = DateTimeUtils()
permission_checker = PermissionChecker()


@access_token_api.post("/v1/access-tokens/add", status_code=201)
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

    _id = access_tokens_collection.insert_one(dict(access_token_model))
    access_token_details_db = all_access_tokens_serializer(
        access_tokens_collection.find({"_id": _id.inserted_id}))
    return {
        "status": "success",
        "access_token": access_token_details_db
    }


@access_token_api.get("/v1/access-tokens/", status_code=200)
async def get_all_access_token(
    page: int = Query(..., description="Page number starting from 0"),
    limit: int = Query(..., description="Number of items per page"),
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    access_tokens_db = all_access_tokens_serializer(access_tokens_collection.find({}))
    if limit == -1:
        return {
            "status": "success",
            "current_page": 1,
            "current_results": len(access_tokens_db),
            "total_results": len(access_tokens_db),
            "all_access_tokens": access_tokens_db
        }
    else:
        start_idx = (int(page) - 1) * limit
        end_idx = start_idx + limit
        access_tokens_to_return = access_tokens_db[start_idx:end_idx]
        return {
            "status": "success",
            "current_page": page,
            "current_results": len(access_tokens_to_return),
            "total_results": len(access_tokens_db),
            "all_access_tokens": access_tokens_to_return
        }


@access_token_api.get("/v1/access-tokens/{access_token_id}", status_code=200)
async def get_specific_access_token(
    access_token_id,
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    access_token_details_db = all_access_tokens_serializer(
        access_tokens_collection.find({"_id": ObjectId(access_token_id)}))

    if access_token_details_db is None:
        return {
            "status": "error",
            "message": "Access token does NOT exists"
        }

    return {
        "status": "success",
        "access_token_details": access_token_details_db
    }


@access_token_api.post("/v1/access-tokens/{access_token_id}", status_code=200)
async def update_specific_access_token(
    access_token_id,
    issuer: Annotated[str, Form()],
    purpose: Annotated[str, Form()],
    access_models: Annotated[str, Form()],
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    access_token_object_id = ObjectId(access_token_id)
    existing_access_token = access_tokens_collection.find_one({"_id": access_token_object_id})

    if existing_access_token is None:
        return {
            "status": "error",
            "message": "Access token does NOT exists"
        }

    existing_access_token['issuer'] = issuer
    existing_access_token['purpose'] = purpose
    access_model_split_list = access_models.split(",")
    access_models = []
    for access_model in access_model_split_list:
        access_models.append(AccessModelsEnum[access_model].value)

    existing_access_token['access_models'] = access_models

    access_tokens_collection.update_one({"_id": access_token_object_id}, {"$set": existing_access_token})

    return {
        "status": "success",
        "message": "Access Token Updated Successfully"
    }


@access_token_api.delete("/v1/access-tokens/{access_token_id}", status_code=200)
async def delete_specific_access_token(
    access_token_id,
    authorization: str = Header(..., description="Bearer Token")
):
    if not utils.users_auth.check_login_token(authorization):
        return {
            "status": "error",
            "message": "unauthorized"
        }

    access_token_object_id = ObjectId(access_token_id)
    existing_access_token = access_tokens_collection.find_one({"_id": access_token_object_id})

    if existing_access_token is None:
        return {
            "status": "error",
            "message": "Access token does NOT exists"
        }

    access_tokens_collection.delete_one({"_id": access_token_object_id})

    return {
        "status": "success",
        "message": "Access Token Deleted Successfully"
    }
