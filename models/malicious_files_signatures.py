from datetime import datetime
from pydantic import BaseModel


class MaliciousFilesSignatures(BaseModel):
    file_signature: str
    file_signature_type: str
    file_category: str
    created_at: datetime = datetime.now()
