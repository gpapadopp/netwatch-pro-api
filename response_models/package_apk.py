from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PackageApksResponseModel(BaseModel):
    id: str
    device_token: str
    package_name: str
    app_name: str
    apk_file: str
    is_malware: Optional[str]
    created_at: datetime
    md5_checksum: str
    access_token_id: str
