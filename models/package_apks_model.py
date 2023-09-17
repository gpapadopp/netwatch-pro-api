from datetime import datetime
from pydantic import BaseModel


class PackageApks(BaseModel):
    device_token: str
    package_name: str
    app_name: str
    apk_file: str
    is_malware: str
    created_at: datetime = datetime.utcnow()
