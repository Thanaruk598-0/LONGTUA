import uuid

from pydantic import AliasChoices, BaseModel, ConfigDict, EmailStr, Field


class AuthSchema(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=lambda value: "".join(
            part.capitalize() if index else part
            for index, part in enumerate(value.split("_"))
        ),
    )


class RegisterRequest(AuthSchema):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    display_name: str | None = Field(
        default=None,
        max_length=100,
        validation_alias=AliasChoices("displayName", "display_name"),
    )
    timezone: str


class UserResponse(AuthSchema):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: EmailStr
    display_name: str
    timezone: str

class LoginRequest(AuthSchema):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
    remember_me: bool = False


class TokenResponse(AuthSchema):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class UserResponseEnvelope(AuthSchema):
    user: UserResponse


class RefreshRequest(AuthSchema):
    refresh_token: str = Field(min_length=1)
