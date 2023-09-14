from enums.access_models_enum import AccessModelsEnum
from config.db import access_tokens_collection
from datetime import datetime


class PermissionChecker:
    def __init__(self):
        return

    def check_model_permission(self, model_name: AccessModelsEnum, api_key, secret_key) -> bool:
        access_model_object = access_tokens_collection.find_one({"api_key": api_key, "secret_key": secret_key})
        if access_model_object is None:
            return False

        if model_name.value in list(access_model_object['access_models']):
            active_until_date = datetime.fromisoformat(str(access_model_object['active_until']))
            now_date = datetime.now()
            if now_date <= active_until_date:
                return True
            else:
                return False
        else:
            return False
