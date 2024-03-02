from datetime import datetime
from pydantic import BaseModel
from typing import Optional


class PackageApks(BaseModel):
    device_token: str
    package_name: str
    app_name: str
    apk_file: str
    is_malware: Optional[str]
    created_at: datetime = datetime.utcnow()
    md5_checksum: str
    access_token_id: str
