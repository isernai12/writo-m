from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql://eirot_user:SDF2ZHchiqwcAhsXLKBKzV2JPDDr7dYT@dpg-d5j189u3jp1c73f6k750-a.singapore-postgres.render.com/eirot"
    jwt_secret: str
    refresh_secret: str
    admin_seed_key: str
    admin_email: str
    admin_password: str
    admin_full_name: str


settings = Settings()
