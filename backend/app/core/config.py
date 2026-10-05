from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_ENV: str = "development"

    DATABASE_URL: str = "sqlite+aiosqlite:///./registry.db"

    # Directory containing all .pkl files + model_registry.json
    MODELS_DIR: str = "../ml_model"

    # Directory where uploaded PDFs are stored (legacy, kept for reference)
    UPLOADS_DIR: str = "../uploads"

    # S3-compatible Object Storage (SeaweedFS)
    S3_ENDPOINT_URL: str = "http://localhost:8333"
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = "documents"
    S3_REGION: str = "us-east-1"

    # Blockchain
    WEB3_PROVIDER_URL: str = "http://127.0.0.1:8545"
    CONTRACT_ADDRESS: str = ""
    DEPLOYER_PRIVATE_KEY: str = (
        "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    )

    # File upload
    MAX_FILE_SIZE_MB: int = 25

    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    class Config:
        env_file = ".env"


settings = Settings()
