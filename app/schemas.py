from pydantic import BaseModel

class UserInput(BaseModel):
    message: str
    assistant_id: str
