from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_VERSION: str = "0.0.1"

    ADMIN_PIN: int = 1234

    POWER_SAVING_TIME: str
    POWER_ON_TIME: str

    REPLICATION_NAME: str
    """The name of the TrueNAS replication task to look for. Must be exactly the same as in TrueNAS."""

    LOG_ALERTS: bool = False
    LOG_DEBUG: bool = False

    IPMI_USER: str
    IPMI_PASSWORD: str
    IPMI_IP: str

    EXCEPTION_DAY: int = 7

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()