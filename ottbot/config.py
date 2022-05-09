# -*- coding=utf-8 -*-
"""Global config."""
__all__: list[str] = ["DatabaseConfig", "Tokens", "FullConfig"]

import abc
import collections.abc as collections
import dataclasses
import logging
import os
import pathlib
import typing

import dotenv
import hikari

ConfigT = typing.TypeVar("ConfigT", bound="Config")
DefaultT = typing.TypeVar("DefaultT")
ValueT = typing.TypeVar("ValueT")


@typing.overload
def _cast_or_else(
    data: collections.Mapping[str, typing.Any],
    key: str,
    cast: collections.Callable[[typing.Any], ValueT],
) -> ValueT:
    ...


@typing.overload
def _cast_or_else(
    data: collections.Mapping[str, typing.Any],
    key: str,
    cast: collections.Callable[[typing.Any], ValueT],
    default: DefaultT | None = None,
) -> ValueT | DefaultT:
    ...


def _cast_or_else(
    data: collections.Mapping[str, typing.Any],
    key: str,
    cast: collections.Callable[[typing.Any], ValueT],
    default: DefaultT | None = None,
) -> ValueT | DefaultT:
    try:
        return cast(data[key])
    except KeyError:
        if default is not None:
            return default

    raise KeyError(f"{key!r} required environment/config key missing")


class Config(abc.ABC):
    """Abstract class that holds configuration data."""

    __slots__ = ()

    @classmethod
    @abc.abstractmethod
    def from_env(cls: type[ConfigT]) -> ConfigT:
        """Generate class from environment variables."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_mapping(cls: type[ConfigT], mapping: collections.Mapping[str, typing.Any], /) -> ConfigT:
        """Generate class from mapping."""
        raise NotImplementedError


@dataclasses.dataclass(kw_only=True, repr=False, slots=True)
class DatabaseConfig(Config):
    """Configuration about a PGSQL database."""

    user: str = "postgres"
    password: str = "postgres"
    database: str = "postgres"
    host: str = "localhost"
    port: int = 5432

    @classmethod
    def from_env(cls: type[ConfigT]) -> ConfigT:
        return cls.from_mapping(os.environ)

    @classmethod
    def from_mapping(cls, mapping: collections.Mapping[str, typing.Any], /) -> "DatabaseConfig":
        return cls(
            user=_cast_or_else(mapping, "DB_USERNAME", str, "postgres"),
            password=_cast_or_else(mapping, "DB_PASSWORD", str, "postgres"),
            database=_cast_or_else(mapping, "DB_NAME", str, "postgres"),
            host=_cast_or_else(mapping, "DB_HOST", str, "localhost"),
            port=_cast_or_else(mapping, "DB_PORT", int, 5432),
        )


@dataclasses.dataclass(kw_only=True, repr=False, slots=True)
class Tokens(Config):
    """Configuration about API tokens."""

    bot: str

    @classmethod
    def from_env(cls: type[ConfigT]) -> ConfigT:
        return cls.from_mapping(os.environ)

    @classmethod
    def from_mapping(cls, mapping: collections.Mapping[str, typing.Any], /) -> "Tokens":
        if "DISCORD_BOT_TOKEN" not in mapping.keys():
            raise KeyError("'DISCORD_BOT_TOKEN' is not a key in `mapping`.")
        if not isinstance(mapping["DISCORD_BOT_TOKEN"], str):
            raise ValueError("'DISCORD_BOT_TOKEN' is not a string.")

        return cls(
            bot=str(mapping["DISCORD_BOT_TOKEN"]),
        )


DEFAULT_CACHE: typing.Final[hikari.api.CacheComponents] = (
    hikari.api.CacheComponents.GUILDS | hikari.api.CacheComponents.GUILD_CHANNELS | hikari.api.CacheComponents.ROLES
)
"""Default cache configuration."""
DEFAULT_INTENTS: typing.Final[hikari.Intents] = hikari.Intents.GUILDS | hikari.Intents.ALL_MESSAGES
"""Default discord indents."""


@dataclasses.dataclass(kw_only=True, repr=False, slots=True)
class FullConfig(Config):
    """The combined config of the bot."""

    database: DatabaseConfig
    tokens: Tokens
    cache: hikari.api.CacheComponents = DEFAULT_CACHE
    emoji_guild: hikari.Snowflake | None = None
    intents: hikari.Intents = DEFAULT_INTENTS
    log_level: int | str | dict[str, typing.Any] | None = logging.INFO
    mention_prefix: bool = True
    owner_only: bool = False
    prefixes: collections.Set[str] = frozenset()
    declare_global_commands: typing.Union[bool, hikari.Snowflake] = True

    @classmethod
    def from_env(cls) -> "FullConfig":
        dotenv.load_dotenv()

        return cls(
            cache=_cast_or_else(os.environ, "cache", hikari.api.CacheComponents, DEFAULT_CACHE),
            database=DatabaseConfig.from_env(),
            emoji_guild=_cast_or_else(os.environ, "emoji_guild", hikari.Snowflake, None),
            intents=_cast_or_else(os.environ, "intents", hikari.Intents, DEFAULT_INTENTS),
            log_level=_cast_or_else(os.environ, "log_level", lambda v: int(v) if v.isdigit() else v, logging.INFO),
            mention_prefix=_cast_or_else(os.environ, "mention_prefix", bool, True),
            owner_only=_cast_or_else(os.environ, "owner_only", bool, False),
            prefixes=_cast_or_else(os.environ, "prefixes", lambda v: frozenset(map(str, v)), frozenset[str]()),
            tokens=Tokens.from_env(),
            declare_global_commands=_cast_or_else(
                os.environ, "declare_global_commands", lambda v: v if isinstance(v, bool) else hikari.Snowflake(v), True
            ),
        )

    @classmethod
    def from_mapping(cls, mapping: collections.Mapping[str, typing.Any], /) -> "FullConfig":
        log_level = mapping.get("log_level", logging.INFO)
        if not isinstance(log_level, (str, int)):
            raise ValueError("Invalid log level found in config")

        elif isinstance(log_level, str):
            log_level = log_level.upper()

        declare_global_commands = mapping.get("declare_global_commands", True)
        if not isinstance(declare_global_commands, bool):
            declare_global_commands = hikari.Snowflake(declare_global_commands)

        return cls(
            cache=_cast_or_else(mapping, "cache", hikari.api.CacheComponents, DEFAULT_CACHE),
            database=DatabaseConfig.from_mapping(mapping["database"]),
            emoji_guild=_cast_or_else(mapping, "emoji_guild", hikari.Snowflake, None),
            intents=_cast_or_else(mapping, "intents", hikari.Intents, DEFAULT_INTENTS),
            log_level=log_level,
            mention_prefix=bool(mapping.get("mention_prefix", True)),
            owner_only=bool(mapping.get("ownerA_only", False)),
            prefixes=frozenset(map(str, mapping["prefixes"])) if "prefixes" in mapping else frozenset(),
            tokens=Tokens.from_mapping(mapping["tokens"]),
            declare_global_commands=declare_global_commands,
        )


def get_config_from_file(file: pathlib.Path | None = None) -> FullConfig:
    """Generate a `FullConfig` instance from a file."""
    import yaml

    if file is None:
        file = pathlib.Path("config.json")
        file = pathlib.Path("config.yaml") if not file.exists() else file

        if not file.exists():
            raise FileNotFoundError("Couldn't find valid yaml or json configuration file")

    data = file.read_text()
    return FullConfig.from_mapping(yaml.safe_load(data))


def load_config() -> FullConfig:
    """Generate a `FullConfig` instance from a predefined file."""
    config_location = os.getenv("OTTBOT_CONFIG_FILE")
    config_path = pathlib.Path(config_location) if config_location else None

    if config_path and not config_path.exists():
        raise FileNotFoundError("Invalid configuration given in environment variables")

    return get_config_from_file(config_path)
