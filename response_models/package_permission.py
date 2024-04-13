from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PackagePermissionsAccessTokenModel(BaseModel):
    issuer: str
    purpose: str
    disabled: bool
    api_key: str
    secret_key: str
    active_until: datetime
    access_models: list
    created_at: datetime


class PackagePermissionsResponseModel(BaseModel):
    id: str
    device_token: str
    package_name: str
    app_name: str
    permissions: list
    certificate_subjects: list
    certificate_issuers: list
    certificate_serial_numbers: list
    certificate_versions: list
    is_malware: str
    created_at: datetime
    access_token_id: str
    access_token_details: Optional[PackagePermissionsAccessTokenModel]
