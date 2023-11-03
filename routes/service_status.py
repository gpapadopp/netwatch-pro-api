import subprocess

from fastapi import APIRouter

service_status_api = APIRouter()


@service_status_api.get("/v1/service-status/vpn-service", status_code=200)
async def get_vpn_service_status():
    try:
        # Use the systemctl command to check the service status
        result = subprocess.check_output(["systemctl", "is-active", "openvpn-server@server.service"])
        status = result.decode().strip()
        if status == "active":
            return {
                "status": "Running"
            }
        else:
            return {
                "status": "Not running"
            }
    except subprocess.CalledProcessError:
        return {"status": "Error checking service status"}
