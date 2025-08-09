"""
Common response schemas
"""
from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel

T = TypeVar('T')

class ErrorResponse(BaseModel):
    """Error response model"""
    code: str
    message: str

class CommonResponse(BaseModel, Generic[T]):
    """Common API response format"""
    isSuccess: bool
    data: Optional[T] = None
    error: Optional[ErrorResponse] = None
    
    @classmethod
    def success(cls, data: Any = None):
        """Create success response"""
        return cls(isSuccess=True, data=data, error=None)
    
    @classmethod
    def fail(cls, code: str, message: str):
        """Create failure response"""
        return cls(
            isSuccess=False,
            data=None,
            error=ErrorResponse(code=code, message=message)
        )