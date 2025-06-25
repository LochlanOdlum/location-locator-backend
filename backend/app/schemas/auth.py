from pydantic import BaseModel

from .user import UserRead


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int | None = None


class SignInResponse(Token):
    user: UserRead
