from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    contraseña: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int | None = None
