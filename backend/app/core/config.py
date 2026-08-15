from urllib.parse import quote_plus

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Config
    APP_NAME: str = "AIRIS Insights"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True

    # MSSQL Config
    MSSQL_HOST: str = ""
    MSSQL_PORT: int = 1433
    MSSQL_DATABASE: str = ""
    MSSQL_USERNAME: str = ""
    MSSQL_PASSWORD: str = ""
    MSSQL_DRIVER: str = "ODBC Driver 18 for SQL Server"

    # Persistence Config (SQLite default for local dev; overridden by POSTGRES_URL in Docker/prod)
    POSTGRES_URL: str = "sqlite:///./dbinsights.db"

    # Redis / Celery Config
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_TASK_TIMEOUT: int = 1800  # 30 minutes max task runtime
    CELERY_WORKER_CONCURRENCY: int = 1  # 1 task at a time per worker to avoid MSSQL overload

    # MSSQL Pool Settings
    MSSQL_POOL_SIZE: int = 5
    MSSQL_MAX_OVERFLOW: int = 2
    MSSQL_QUERY_TIMEOUT: int = 30

    # Sampling Settings
    PROFILE_SAMPLE_SIZE: int = 100
    PROFILE_MAX_SAMPLE_SIZE: int = 10000

    # Analysis Orchestration Settings
    ANALYSIS_MAX_CONCURRENT_TABLES: int = 3
    ANALYSIS_SAMPLE_TINY: int = 1000
    ANALYSIS_SAMPLE_SMALL: int = 1000
    ANALYSIS_SAMPLE_MEDIUM: int = 2000
    ANALYSIS_SAMPLE_LARGE: int = 3000
    ANALYSIS_SAMPLE_VERY_LARGE: int = 5000

    ANALYSIS_TINY_TABLE_MAX_ROWS: int = 1000
    ANALYSIS_SMALL_TABLE_MAX_ROWS: int = 10000
    ANALYSIS_MEDIUM_TABLE_MAX_ROWS: int = 100000
    ANALYSIS_LARGE_TABLE_MAX_ROWS: int = 1000000

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def mssql_url(self) -> str:
        """Constructs the SQLAlchemy connection URL for MSSQL."""
        if not self.MSSQL_HOST:
            return ""  # Graceful failure if not set up yet

        # Encode password in case of special characters
        password = quote_plus(self.MSSQL_PASSWORD)
        driver = self.MSSQL_DRIVER.replace(" ", "+")

        # Adding TrustServerCertificate=yes to help with initial local development connections
        # if the certificate isn't properly trusted on the local machine
        return (
            f"mssql+pyodbc://{self.MSSQL_USERNAME}:{password}@{self.MSSQL_HOST}:{self.MSSQL_PORT}"
            f"/{self.MSSQL_DATABASE}?driver={driver}&TrustServerCertificate=yes"
        )


settings = Settings()
