from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # FastAPI
    api_title: str = "RAG API Backend"
    api_version: str = "1.0.0"
    debug: bool = True

    # Pinecone
    pinecone_api_key: str = ""
    pinecone_environment: str = "us-west1-gcp"
    pinecone_index_name: str = "rag-queries"

    # GCP Inference Backend
    inference_function_url: str = ""
    inference_function_key: str = ""

    # Cache settings
    cache_ttl_seconds: int = 86400  # 24 hours
    similarity_threshold: float = 0.95  # For cache hits

    # API settings
    max_query_length: int = 1000
    max_results: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
