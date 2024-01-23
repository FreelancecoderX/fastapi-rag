from fastapi import APIRouter, Query, Depends, Path
from typing import Annotated

from models import ChatResponse
from dependencies import get_query_engine

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/{chatId}/answer", response_model=ChatResponse)
async def query_index(
    chatId: Annotated[int, Path(description="Chat Id")],
    question: Annotated[str, Query(description="The question to query")],
    query_engine=Depends(get_query_engine),
):
    result = query_engine.query(question)

    return {
        "chat_id": chatId,
        "answer": result.response,
        "sources": result.get_formatted_sources(),
    }
