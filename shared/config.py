"""Configuration using pydantic-settings."""
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Azure OpenAI
    azure_openai_endpoint: str = Field(default="https://your-openai.openai.azure.com/", env="AZURE_OPENAI_ENDPOINT")
    azure_openai_api_key: str = Field(default="your-api-key", env="AZURE_OPENAI_API_KEY")
    azure_openai_api_version: str = Field(default="2024-02-01", env="AZURE_OPENAI_API_VERSION")
    azure_openai_deployment: str = Field(default="gpt-4o", env="AZURE_OPENAI_DEPLOYMENT")

    # Azure Service Bus
    service_bus_connection_string: str = Field(default="", env="SERVICE_BUS_CONNECTION_STRING")
    service_bus_namespace: str = Field(default="", env="SERVICE_BUS_NAMESPACE")

    # Cosmos DB
    cosmos_endpoint: str = Field(default="https://your-cosmos.documents.azure.com:443/", env="COSMOS_ENDPOINT")
    cosmos_key: str = Field(default="your-cosmos-key", env="COSMOS_KEY")
    cosmos_database: str = Field(default="contoso-research", env="COSMOS_DATABASE")
    cosmos_reports_container: str = Field(default="research-reports", env="COSMOS_REPORTS_CONTAINER")

    # Azure Blob Storage
    storage_account_name: str = Field(default="your-storage", env="STORAGE_ACCOUNT_NAME")
    storage_account_key: str = Field(default="your-storage-key", env="STORAGE_ACCOUNT_KEY")
    storage_container_name: str = Field(default="research-reports", env="STORAGE_CONTAINER_NAME")

    # Feature flags
    local_mode: bool = Field(default=True, env="LOCAL_MODE")  # Run without Service Bus
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    return Settings()
