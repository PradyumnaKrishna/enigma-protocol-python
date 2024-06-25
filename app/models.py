from pydantic import BaseModel, Field


class LoginResponse(BaseModel):
    user: str


class ConnectResponse(BaseModel):
    user: str
    publicKey: str


class TransmissionData(BaseModel):
    from_: str = Field(..., alias="from")
    to: str
    payload: str

class VersionResponse(BaseModel):
    version: str
