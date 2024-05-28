from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Define the Settings class
class Settings(BaseSettings):
    model_config = ConfigDict( env_file=".env")

    admin_host: str
    admin_port: int = Field(default=5432, env='ADMIN_PORT')
    admin_password: str 
    admin_database: str
    admin_user: str 
    admin_algorithm: str 
    admin_access_token_expire_minutes: int = Field(default=55, env='ADMIN_ACCESS_TOKEN_EXPIRE_MINUTES') 
    admin_database_url: str
    admin_oauth2_secret_key: str
    openai_api_key: str


# Create an instance of the Settings class
settings = Settings()
