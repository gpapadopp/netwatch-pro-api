from datetime import datetime
from pydantic import BaseModel


class MaliciousFilesSignaturesResponseModel(BaseModel):
    id: str
    file_signature: str
    file_signature_type: str
    file_category: str
    created_at: datetime
