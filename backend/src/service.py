from llama_index import StorageContext, ServiceContext, LLMPredictor
from llama_index.indices.loading import load_index_from_storage
from llama_index.llms import TogetherLLM
from pymongo import MongoClient

from utils import (
    build_pinecone_vector_store,
    build_mongo_index,
    buildVectorIndex,
    createQueryEngine,
    getExistingLlamaIndexes,
)
from config import settings

index_store = build_mongo_index(uri=settings.MONGO_URI)
vector_store = build_pinecone_vector_store(
    api_key=settings.PINECONE_API_KEY, index=settings.PINECONE_INDEX
)

llm = TogetherLLM(model=settings.MODEL, api_key=settings.TOGETHER_API_KEY)
llm_predictor = LLMPredictor(llm=llm)

service_context = ServiceContext.from_defaults(
    llm_predictor=llm_predictor,
    embed_model="local:BAAI/bge-small-en-v1.5",
)

storage_context = StorageContext.from_defaults(
    index_store=index_store, vector_store=vector_store
)

mongoIndex = None


def initialize_index():
    database = MongoClient(host=settings.MONGO_URI).get_database()
    existing_indexes = getExistingLlamaIndexes(database=database)

    global mongoIndex

    if len(existing_indexes) > 0:
        print("Loading existing index...")

        mongoIndex = load_index_from_storage(
            service_context=service_context,
            storage_context=storage_context,
            llm_predictor=llm_predictor,
            index_id="mongo-index",
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