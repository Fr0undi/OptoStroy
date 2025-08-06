from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    
    base_url: str = Field(default = "https://optostroy.com")
    
    mongo_url: str = Field(default = "mongodb://127.0.0.1:27017/")
    db_name: str = Field(default = "OptoStroy")
    collection_name: str = Field(default = "products")

    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
settings = Settings()