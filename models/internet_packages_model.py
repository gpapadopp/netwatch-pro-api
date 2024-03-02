from datetime import datetime
from pydantic import BaseModel


class InternetPackages(BaseModel):
    device_token: str
    source_ip: str
    destination_ip: str
    source_mac_address: str
    destination_mac_address: str
    header_type: str
    raw_header: str
    raw_payload: str
    created_at: datetime = datetime.utcnow()
    access_token_id: str
