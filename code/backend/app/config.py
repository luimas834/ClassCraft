"""Settings for the backend.
Every value comes from an environment variable, listed in .env.example.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The settings the backend needs, read once when the app starts."""

    # The version shown by the health endpoint and in the API documentation.
    app_version: str = "0.1.0"

    database_url: str = "postgresql+psycopg://classcraft:change-me@db:5432/classcraft"

    secret_key: str = "change-me-to-a-long-random-string"
    access_token_minutes: int = 720
    cookie_secure: bool = False

    first_admin_email: str = "committee@example.edu"
    first_admin_password: str = "change-me-now"
    first_admin_name: str = "Routine Committee"

    app_timezone: str = "Asia/Dhaka"
    seed_data: str = "demo"

    solver_default_time_limit: int = 60
    solver_max_time_limit: int = 600

    # Extra addresses allowed to call the API. Empty, because the web app and
    # the API share one address in development and in production.
    cors_origins: str = ""
    log_level: str = "info"

    # extra="ignore" lets one .env file serve the database and the worker too.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
