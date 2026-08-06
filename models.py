from pydantic import BaseModel
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