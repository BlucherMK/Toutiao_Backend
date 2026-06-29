#校验
from pydantic import BaseModel

class UserRequest(BaseModel):
    username: str
    password: str