from llama_index import (
    StorageContext,
    ServiceContext,
    SimpleDirectoryReader,
    VectorStoreIndex,
)
from llama_index.llms import ChatMessage, MessageRole
from llama_index.storage.index_store import MongoIndexStore
from llama_index.vector_stores import PineconeVectorStore
from pinecone import Pinecone

from chat.constants import TOP_K, MONGODB_INDEX


def build_pinecone_vector_store(api_key: str, index: str):
    pc = Pinecone(api_key=api_key)
    pinecone_index = pc.Index(index)
    vector_store = PineconeVectorStore(pinecone_index=pinecone_index)
    return vector_store


def build_mongo_index(uri: str):
    index_store = MongoIndexStore.from_uri(uri=uri)
    return index_store


def buildVectorIndex(
    files: str, service_context: ServiceContext, storage_context: StorageContext
):
    reader = SimpleDirectoryReader(input_files=[files])

    documents = reader.load_data()

    index = VectorStoreIndex.from_documents(
        documents, service_context=service_context, storage_context=storage_context
    )

    index.set_index_id(MONGODB_INDEX)

    return index


def createQueryEngine(index):
    return index.as_query_engine(response_mode="simple_summarize", top_k=TOP_K)


def get_service_context(service_context: ServiceContext):
    return service_context


def getExistingLlamaIndexes(database):
    """
    Get the existing Llama Indexes
    """

    indexes = []

    cursor = database["index_store/data"].find({})

    for item in cursor:
        indexes.append(item)

    return indexes

def getHistoryRole(message):
    """
    Get the role of the message in the chat history
    """

    if message['role'] == 'user':
        return MessageRole.USER
    else:
        return MessageRole.ASSISTANT
    
def convertMongoChat(chat_history):
    """
    Convert chat history from MongoDB to the format required by the chat engine
    """

    chat = []

    for message in chat_history:
        chat.append(ChatMessage(
        role=getHistoryRole(message), 
        content=message['message'],
    ))

    return chat