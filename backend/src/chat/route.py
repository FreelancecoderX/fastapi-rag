from bson import ObjectId
from llama_index.memory import ChatMemoryBuffer
from llama_index.chat_engine import ContextChatEngine
from fastapi import APIRouter, Query, Depends, Path, status
from fastapi.responses import JSONResponse
from typing import Annotated

from chat.config import SYSTEM_PROMPT
from chat.service import (
    initialize_index,
    create_chat,
    retrieve_user_chat_history,
    parse_mongo_item_to_json,
    get_user_chat,
    retrieve_chat_history,
    send_and_save_response,
    update_message_feedback,
    service_context,
)

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/guest")
async def get_guest_chat():
    chat = await create_chat(str(ObjectId()), "guest")
    return JSONResponse(
        content={"_id": str(chat["_id"])}, status_code=status.HTTP_200_OK
    )


@router.get("/me")
async def get_my_chat(current_user: dict):
    chat = await get_user_chat(current_user["_id"])

    if chat is None:
        chat = await create_chat(str(current_user["_id"]), current_user["role"])

    return JSONResponse(
        content=parse_mongo_item_to_json(chat), status_code=status.HTTP_200_OK
    )


@router.get("/me/history")
async def get_my_chat_history(current_user: dict):
    chat = await get_user_chat(current_user["_id"])
    chat_history = await retrieve_user_chat_history(str(chat["_id"]))
    return JSONResponse(content=chat_history, status_code=status.HTTP_200_OK)


@router.put("/message/{message_id}/feedback")
async def set_message_feedback(message_id: str, feedback: str):
    if feedback not in ["good", "bad"]:
        return JSONResponse(
            content="Invalid feedback (use good or bad)", status_code=400
        )

    updated_message = await update_message_feedback(message_id, feedback)

    del updated_message["_id"]
    del updated_message["chatId"]

    return JSONResponse(content=updated_message, status_code=200)


@router.get("/{chat_id}/q")
async def query_index(
    chat_id: Annotated[int, Path(description="Chat Id")],
    q: Annotated[str, Query(description="Question")],
    query_engine=Depends(initialize_index),
):
    if not q:
        return JSONResponse(
            content="No text found, please include a ?q=example parameter in the URL",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    history = await retrieve_chat_history(chat_id)
    memory = ChatMemoryBuffer.from_defaults(chat_history=history)

    chat_engine = ContextChatEngine.from_defaults(
        retriever=query_engine,
        memory=memory,
        service_context=service_context,
        system_prompt=SYSTEM_PROMPT,
        verbose=True,
    )

    response = await chat_engine.stream_chat(message=q)
    return JSONResponse(
        content=send_and_save_response(response, chat_id, q),
        media_type="application/json",
    )
