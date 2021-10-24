from pydantic import BaseModel


class AWSTag(BaseModel):
    key: str
    value: str


