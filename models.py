from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional, Literal
from datetime import date

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

class Booking(BaseModel):
    id: Optional[int] = None
    attractionId: int
    date: date 
    time: Literal["上半天", "下半天"] 
    price: Literal['新台幣 2000 元', '新台幣 2500 元']
    email: EmailStr

class BookingRequest(BaseModel):
    attractionId: int
    date: date 
    time: Literal["morning", "afternoon"] 
    price: Literal[2000, 2500]