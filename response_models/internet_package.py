from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InternetPackageAccessTokenModel(BaseModel):
    issuer: str
    purpose: str
    disabled: bool
    api_key: str
    secret_key: str
    active_until: datetime
    access_models: list
    created_at: datetime


class InternetPackagesResponseModel(BaseModel):
    id: str
    device_token: str
    source_ip: str
    destination_ip: str
    source_mac_address: str
    destination_mac_address: str
    header_type: str
    raw_header: str
    raw_payload: str
    created_at: datetime
    access_token_id: str
    access_token_details: Optional[InternetPackageAccessTokenModel]
