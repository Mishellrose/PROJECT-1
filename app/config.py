from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_hostname: str
    database_port:str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    RAZORPAY_KEY_ID: str
    RAZORPAY_KEY_SECRET: str
    RAZORPAY_WEBHOOK_SECRET: str
    WEBHOOK_URL: str  

    SUBSCRIPTION_AMOUNT_ONE_MONTH: Optional[int] = 100     # default ₹100
    SUBSCRIPTION_AMOUNT_THREE_MONTH: Optional[int] = 300



    class Config():
        env_file = ".env"

settings = Settings()

       