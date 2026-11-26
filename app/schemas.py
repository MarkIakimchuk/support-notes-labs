from pydantic import BaseModel, ConfigDict, Field


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
