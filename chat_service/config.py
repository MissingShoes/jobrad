"""Configuration module for the application using typed settings."""

import typed_settings


@typed_settings.settings
class Quart:
    DEBUG: bool
    ENV: str
    TESTING: bool


@typed_settings.settings
class Database:
    uri: str
    echo: bool


@typed_settings.settings
class Settings:
    quart: Quart
    database: Database
    base_path: str

    default_message: str


settings = typed_settings.load_settings(
    cls=Settings,
    loaders=[
        typed_settings.FileLoader(
            files=[typed_settings.find("config/config.toml")],
            env_var="CONFIG",  # allows to overwrite the path to the config file
            formats={
                "*.toml": typed_settings.TomlFormat("chat-service"),
            },
        ),
        typed_settings.EnvLoader(prefix=""),
    ],
)
