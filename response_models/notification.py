from datetime import datetime
from pydantic import BaseModel


class NotificationResponseModel(BaseModel):
    id: str
    title: str
    context: str
    banner: str
    disabled: bool
    created_at: datetime
