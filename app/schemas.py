from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator


class PostInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=3, max_length=160)
    symptoms: str = Field(min_length=5, max_length=2000)
    solution: str = Field(min_length=5, max_length=4000)


class PostView(PostInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class UserInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    username: str = Field(pattern=r"^[a-z][a-z0-9_]{2,31}$")
    display_name: str = Field(min_length=2, max_length=100)


class UserView(UserInput):
    model_config = ConfigDict(from_attributes=True)

    id: int


class Credentials(BaseModel):
    username: str = Field(pattern=r"^[a-z][a-z0-9_]{2,31}$")
    password: str = Field(min_length=8, max_length=72, repr=False)

    @field_validator("password")
    @classmethod
    def check_bytes(cls, value: str):
        if len(value.encode()) > 72:
            raise ValueError("Пароль должен занимать не более 72 байт в UTF-8")
        return value


class Registration(Credentials):
    model_config = ConfigDict(extra="forbid")

    display_name: Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=100)]


class RefreshInput(BaseModel):
    refresh_token: str = Field(min_length=1, max_length=2048, repr=False)


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: Literal["bearer"] = "bearer"
