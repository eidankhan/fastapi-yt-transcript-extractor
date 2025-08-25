from pydantic import BaseModel, EmailStr
from typing import Any, Dict, Optional

class SuccessResponse(BaseModel):
    status: str = "success"
    code: int = 200
    data: Dict[str, Any]

class ErrorResponse(BaseModel):
    status: str = "error"
    code: int
    message: str
    error: Optional[str] = None

from pydantic import BaseModel, EmailStr

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    api_key: str
    tier: str

    class Config:
        orm_mode = True

