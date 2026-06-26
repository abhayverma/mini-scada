from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # No defaults. The app will crash on startup if these aren't in .env!
    MQTT_BROKER: str 
    REDIS_URL: str 
    DATABASE_URL: str 
    SECRET_KEY: str 
    
    # Defaults are okay for non-critical operational configs
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
