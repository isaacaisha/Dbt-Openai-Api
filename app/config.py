import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Define the Settings class
class Settings(BaseSettings):
    host: str
    port: str
    password: str 
    database: str
    user: str 
    database_secret_key: str
    algorithm: str 
    access_token_expire_minutes: str 

    class Config:
        env_file = ".env_database"

# Create an instance of the Settings class
settings = Settings()
