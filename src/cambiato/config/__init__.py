r"""The configuration of Cambiato."""

from cambiato.config.config import ConfigManager, load_config
from cambiato.config.core import (
    BITWARDEN_PASSWORDLESS_API_URL,
    CONFIG_DIR,
    CONFIG_FILE_ENV_VAR,
    CONFIG_FILE_PATH,
    CONFIG_FILENAME,
    PROG_NAME,
    BaseConfigModel,
    BitwardenPasswordlessConfig,
    DatabaseConfig,
    Language,
)

# The Public API
__all__ = [
    # config
    'ConfigManager',
    'load_config',
    # core
    'BITWARDEN_PASSWORDLESS_API_URL',
    'CONFIG_DIR',
    'CONFIG_FILE_ENV_VAR',
    'CONFIG_FILE_PATH',
    'CONFIG_FILENAME',
    'PROG_NAME',
    'BaseConfigModel',
    'BitwardenPasswordlessConfig',
    'DatabaseConfig',
    'Language',
]
