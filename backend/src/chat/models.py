from pydantic import BaseModel

class ChatResponse(BaseModel):
    chat_id: int
    answer: str
    sources: str