from pydantic import BaseModel


class AuthenticationResponse(BaseModel):
    token: str
    type: str
