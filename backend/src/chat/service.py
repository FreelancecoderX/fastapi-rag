import certifi
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


def initialize_index():
    ca = certifi.where()

    client = MongoClient(
        host=settings.MONGO_URI,
        server_api=ServerApi(settings.MONGO_SERVER_API),
        tlsCAFile=ca,
    )
    database = client.get_default_database()
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
