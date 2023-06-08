from datetime import datetime
from pydantic import BaseModel


class PackagePermissions(BaseModel):
    device_token: str
    package_name: str
    app_name: str
    permissions: list
    certificate_subjects: list
    certificate_issuers: list
    certificate_serial_numbers: list
    certificate_versions: list
    created_at: datetime = datetime.utcnow()
