from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    GROQ_API_KEY: str
    VECTOR_PATH: str = "vectorstore/faiss_index"
    UPLOAD_DIR: str = "uploads"

    class Config:
        env_file = ".env"

settings = Settings()