from pydantic import BaseModel
from models.package_apks_model import PackageApks


class PackageApksResponsePredict(BaseModel):
    status: str
    is_malware: bool
    package_apk: PackageApks
