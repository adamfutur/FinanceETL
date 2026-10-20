import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # API Keys
    EXCHANGE_RATE_API_KEY: str = Field(default="demo_key")
    BASE_CURRENCY: str = Field(default="GBP")
    TARGET_CURRENCIES: list = Field(default=["USD", "EUR", "MAD"])
    
    # Local DB
    POSTGRES_USER: str = Field(default="postgres")
    POSTGRES_PASSWORD: str = Field(default="postgres")
    POSTGRES_DB: str = Field(default="finance_db")
    POSTGRES_HOST: str = Field(default="localhost")
    POSTGRES_PORT: int = Field(default=5432)
    
    # GCP
    GCP_PROJECT_ID: str = Field(default="")
    GCP_DATASET_ID: str = Field(default="finance_dw")
    GCP_BUCKET_NAME: str = Field(default="")
    
    # App Settings
    LOG_LEVEL: str = Field(default="INFO")
    RAW_DATA_PATH: Path = Field(default=BASE_DIR / "data" / "raw")
    PROCESSED_DATA_PATH: Path = Field(default=BASE_DIR / "data" / "processed")
    DATASET_URL: str = Field(default="https://archive.ics.uci.edu/ml/machine-learning-databases/00352/Online%20Retail.xlsx")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
