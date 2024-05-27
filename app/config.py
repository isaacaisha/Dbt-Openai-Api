from pydantic import ConfigDict
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

# Define the Settings class
class Settings(BaseSettings):
    model_config = ConfigDict( env_file=".env")

    admin_host: str
    admin_port: int
    admin_password: str 
    admin_database: str
    admin_user: str 
    admin_algorithm: str 
    admin_access_token_expire_minutes: int 
    admin_database_url: str
    admin_oauth2_secret_key: str
    openai_api_key: str


# Create an instance of the Settings class
settings = Settings()
