from pydantic import BaseModel

class ChatResponse(BaseModel):
    chat_id: str
    answer: str
    sources: str