from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

###
class Success(BaseModel):
    ok: bool = True

class Error(BaseModel):
    error: bool = True
    message: str

###
class Attraction(BaseModel):
    id: int
    name: str
    category: str
    description: str
    address: str
    transport: str
    mrt: Optional[str] = None
    lat: float
    lng: float
    images: List[str]

class User(BaseModel):
    # id: Optional[int] = None
    name: Optional[str] = None # 登入時只需要email，不需要name
    email: EmailStr
    hashed_password: str = Field(..., max_length=70) # default="default"
    # role: str = Field(default="default", max_length=20)

class UserSignIn(BaseModel):
    email: EmailStr
    password: str = Field(..., max_length=70)

class UserSignUp(BaseModel):
    name: str
    email: EmailStr
    password: str = Field(..., max_length=70)