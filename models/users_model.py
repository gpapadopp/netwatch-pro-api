from datetime import datetime
from pydantic import BaseModel


class UsersModel(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: str
    disabled: bool
    created_at: datetime = datetime.utcnow()
