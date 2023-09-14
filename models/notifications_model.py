from datetime import datetime
from pydantic import BaseModel


class NotificationsModel(BaseModel):
    title: str
    context: str
    banner: str
    disabled: bool
    created_at: datetime = datetime.utcnow()
