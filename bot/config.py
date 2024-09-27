from dataclasses import dataclass

from environs import Env

@dataclass
class TgBot:
    token: str


@dataclass
class Postgres:
    postgres_host: str
    postgres_db: str
    postgres_password: str
    postgres_port: int
    postgres_user: str

    def get_connection_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

@dataclass
class Redis:
    redis_host: str
    redis_port: int
    redis_db: int
    redis_data: str

@dataclass
class AdminConfig:
    admin_login: str
    admin_password: str
    secret_key: str

@dataclass
class OpenAI:
    api_token: str

@dataclass
class Config:
    tg_bot: TgBot
    postgres_db: Postgres
    redis_db: Redis
    admin_config: AdminConfig
    open_ai: OpenAI



def load_config(path: str | None = None) -> Config:
    env = Env()
    env.read_env(path)
    return Config(
        tg_bot=TgBot(token=env("BOT_TOKEN")),
        postgres_db=Postgres(
            postgres_host=env("POSTGRES_HOST"),
            postgres_db=env("POSTGRES_DB"),
            postgres_password=env("POSTGRES_PASSWORD"),
            postgres_port=env.int("POSTGRES_PORT"),
            postgres_user=env("POSTGRES_USER")
        ),
        redis_db=Redis(
            redis_host=env("REDIS_HOST"),
            redis_port=env("REDIS_PORT"),
            redis_db=env("REDIS_DB"),
            redis_data=env("REDIS_DATA")
        ),
        admin_config=AdminConfig(
        admin_login=env("ADMIN_LOGIN"),
        admin_password=env("ADMIN_PASSWORD"),
        secret_key=env("SECRET_KEY"),
        ),
        open_ai=OpenAI(api_token=env("OPENAI_API"))
    )
