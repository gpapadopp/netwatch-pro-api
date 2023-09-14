from fastapi import APIRouter, Form
from typing import Annotated
from models.access_tokens_model import AccessTokensModel
from datetime import datetime
from utils.date_time_utils import DateTimeUtils
from schemas.access_tokens_schema import all_access_tokens_serializer
from config.db import access_tokens_collection
from enums.access_models_enum import AccessModelsEnum
from utils.permission_checker import PermissionChecker
import uuid

access_token_api = APIRouter()
date_time_util_instance = DateTimeUtils()
permission_checker = PermissionChecker()


@access_token_api.post("/api/v1/access-tokens/add", status_code=201)
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
