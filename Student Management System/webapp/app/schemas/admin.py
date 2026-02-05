from pydantic import BaseModel

class AdminCreate(BaseModel):
    username: str
    password: str

class AdminLogin(BaseModel):
    username: str
    password: str

class AdminUpdate(BaseModel):
    username: str | None = None
    password: str | None = None

class AdminRead(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True
