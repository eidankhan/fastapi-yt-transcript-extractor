from pydantic import BaseModel
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
