from fastapi import APIRouter, Query, Depends, Path
from typing import Annotated

from chat.models import ChatResponse
from chat.service import initialize_index

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/{chatId}/q", response_model=ChatResponse)
def query_index(
    chatId: Annotated[int, Path(description="Chat Id")],
    q: Annotated[str, Query(description="Question")],
    query_engine=Depends(initialize_index),
):
    result = query_engine.query(q)

    return {
        "chat_id": chatId,
        "answer": result.response,
        "sources": result.get_formatted_sources(),
    }
