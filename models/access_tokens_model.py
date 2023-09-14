from datetime import datetime
from pydantic import BaseModel


class AccessTokensModel(BaseModel):
    issuer: str
    purpose: str
    disabled: bool
    api_key: str
    secret_key: str
    active_until: datetime
    access_models: list
    created_at: datetime = datetime.utcnow()
