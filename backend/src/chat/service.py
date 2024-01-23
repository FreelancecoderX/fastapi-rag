import certifi
from bson import ObjectId
from datetime import datetime
from llama_index.embeddings import HuggingFaceEmbedding
from llama_index import StorageContext, ServiceContext, LLMPredictor
from llama_index.indices.loading import load_index_from_storage
from llama_index.llms import TogetherLLM
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from chat.utils import (
    build_pinecone_vector_store,
    build_mongo_index,
    buildVectorIndex,
    createQueryEngine,
    getExistingLlamaIndexes,
)
from config import settings
from chat.constants import MONGODB_INDEX
from chat.utils import convertMongoChat

index_store = build_mongo_index(uri=settings.MONGO_URI)
vector_store = build_pinecone_vector_store(
    api_key=settings.PINECONE_API_KEY, index=settings.PINECONE_INDEX
)

llm = TogetherLLM(model=settings.MODEL, api_key=settings.TOGETHER_API_KEY)
llm_predictor = LLMPredictor(llm=llm)

embed_model = HuggingFaceEmbedding(model_name=settings.EMBEDDING_MODEL)

service_context = ServiceContext.from_defaults(
    llm_predictor=llm_predictor,
    embed_model=embed_model,
)

storage_context = StorageContext.from_defaults(
    index_store=index_store, vector_store=vector_store
)

mongoIndex = None

ca = certifi.where()
client = MongoClient(
    host=settings.MONGO_URI,
    server_api=ServerApi(settings.MONGO_SERVER_API),
    tlsCAFile=ca,
)

database = client.get_default_database()


def initialize_index():
    existing_indexes = getExistingLlamaIndexes(database=database)

    global mongoIndex

    if len(existing_indexes) > 0:
        print("Loading existing index...")

        mongoIndex = load_index_from_storage(
            service_context=service_context,
            storage_context=storage_context,
            llm_predictor=llm_predictor,
            index_id=MONGODB_INDEX,
        )

        return createQueryEngine(mongoIndex)
    else:
        print("Building index...")

        mongoIndex = buildVectorIndex(
            files=settings.FILES,
            service_context=service_context,
            storage_context=storage_context,
        )

        return createQueryEngine(mongoIndex)


async def create_chat(user_id, role):
    database.chats.insert_one(
        {"userId": ObjectId(user_id), "role": role, "createdAt": datetime.now()}
    )
    return database.chats.find_one({"userId": ObjectId(user_id)})


async def retrieve_user_chat_history(chat_id: str):
    messages = []

    cursor = await database.chatmessages.find({"chatId": ObjectId(chat_id)}).sort(
        "createdAt", 1
    )

    for item in cursor:
        messages.append(parse_mongo_item_to_json(item))

    return messages


def parse_mongo_item_to_json(item):
    return {k: v for k, v in item.items() if k != "_id"}


async def get_user_by_id(id: str):
    return database["users"].find_one({"_id": ObjectId(id)})


async def get_user_chat(user_id: str):
    return database.chats.find_one({"userId": ObjectId(user_id)})


async def send_and_save_response(response, chat_id, query_text):
    response_content = []

    for token in response.response_gen:
        response_content.append(token)

    user_message = insert_message_in_chat(chat_id, query_text, "user")
    bot_response = insert_message_in_chat(chat_id, str(response), "assistant")

    response_content.append(
        {
            "user_message": str(user_message.inserted_id),
            "bot_response": str(bot_response.inserted_id),
        }
    )

    return response_content


async def get_chat_history(chatId):
    messages = (
        database.chatmessages.find({"chatId": ObjectId(chatId)})
        .sort("createdAt", -1)
        .limit(4)
    )

    return list(messages)


async def retrieve_chat_history(chat_id: str):
    chat_history = await get_chat_history(chat_id)
    return convertMongoChat(chat_history)


async def insert_message_in_chat(chat_id: str, message: str, role: str):
    return database.chatmessages.insert_one(
        {
            "chatId": ObjectId(chat_id),
            "message": message,
            "role": role,
            "createdAt": datetime.now(),
        }
    )


async def update_message_feedback(message_id: str, feedback: str):
    await database.chatmessages.update_one(
        {"_id": ObjectId(message_id)}, {"$set": {"feedback": feedback}}
    )
    return database.chatmessages.find_one({"_id": ObjectId(message_id)})
