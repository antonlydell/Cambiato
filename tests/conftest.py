r"""Fixtures for testing Cambiato."""

# Standard library
import io
from copy import deepcopy
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

# Third party
import pytest
from sqlalchemy import make_url

# Local
import cambiato.config.config
from cambiato.config import (
    BITWARDEN_PASSWORDLESS_API_URL,
    LOGGING_DEFAULT_DATETIME_FORMAT,
    LOGGING_DEFAULT_FORMAT,
    Language,
    LogLevel,
    Stream,
)
from tests.config import STATIC_FILES_CONFIG_BASE_DIR


@pytest.fixture
def remove_config_file_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    r"""Remove the config file environment variable CAMBIATO_CONFIG_FILE."""

    monkeypatch.delenv(cambiato.config.config.CONFIG_FILE_ENV_VAR, raising=False)


@pytest.fixture
def config_data(tmp_path: Path) -> tuple[str, dict[str, Any]]:
    r"""A Cambiato configuration with a SQLite database.

    Returns
    -------
    config_data_str : str
        The configuration as a string of toml.

    config_exp : dict[str, Any]
        The expected configuration after loading and parsing `config_data_str`.
    """

    source_filename = 'Cambiato.toml'
    source_config_file_path = STATIC_FILES_CONFIG_BASE_DIR / source_filename

    assert source_config_file_path.exists(), f'File "{source_config_file_path}" does not exist!'

    config_data_str = source_config_file_path.read_text()

    db_path = tmp_path / 'Cambiato.db'
    db_url_str = f'sqlite:///{db_path!s}'
    web_log_file_path = tmp_path / 'Cambiato.log'

    config_data_str = config_data_str.replace(':db_url', db_url_str).replace(
        ':web_log_file_path', str(web_log_file_path)
    )

    database_config = {
        'url': tuple(make_url(db_url_str)),
        'autoflush': False,
        'expire_on_commit': True,
        'create_database': True,
        'connect_args': {'timeout': 30},
        'engine_config': {'echo': True},
    }

    bwp_config = {
        'public_key': 'bwp_public_key',
        'private_key': 'bwp_private_key',
        'url': BITWARDEN_PASSWORDLESS_API_URL,
    }
    logging_config = {
        'disabled': False,
        'min_log_level': LogLevel.INFO,
        'format': LOGGING_DEFAULT_FORMAT,
        'datetime_format': LOGGING_DEFAULT_DATETIME_FORMAT,
        'stream': {
            'stdout': {
                'stream': Stream.STDOUT,
                'disabled': False,
                'min_log_level': LogLevel.INFO,
                'format': LOGGING_DEFAULT_FORMAT,
                'datetime_format': LOGGING_DEFAULT_DATETIME_FORMAT,
            },
            'stderr': {
                'stream': Stream.STDERR,
                'disabled': False,
                'min_log_level': LogLevel.ERROR,
                'format': LOGGING_DEFAULT_FORMAT,
                'datetime_format': LOGGING_DEFAULT_DATETIME_FORMAT,
            },
        },
        'file': {
            'web': {
                'unique': False,
                'path': web_log_file_path,
                'max_bytes': 1_200_000,
                'backup_count': 5,
                'mode': 'a',
                'encoding': 'UTF-8',
                'disabled': False,
                'min_log_level': LogLevel.INFO,
                'format': LOGGING_DEFAULT_FORMAT,
                'datetime_format': LOGGING_DEFAULT_DATETIME_FORMAT,
            }
        },
        'email': None,
    }

    config_exp = {
        'timezone': ZoneInfo('Europe/Stockholm'),
        'languages': (Language.EN,),
        'default_language': Language.EN,
        'database': database_config,
        'bwp': bwp_config,
        'logging': logging_config,
    }

    return config_data_str, config_exp


@pytest.fixture
def config_file(
    config_data: tuple[str, dict[str, Any]], tmp_path: Path
) -> tuple[Path, str, dict[str, Any]]:
    r"""A Cambiato config file.

    Returns
    -------
    config_file_path : pathlib.Path
        The path to the config file.

    config_data_str : str
        The configuration written to `config_file_path` as a string of toml.

    config_exp : dict[str, Any]
        The expected configuration after loading `config_file_path`.
    """

    config_data_str, config_exp_original = config_data

    config_file_path = tmp_path / 'Cambiato.toml'
    config_file_path.write_text(config_data_str)

    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = config_file_path

    return config_file_path, config_data_str, config_exp


@pytest.fixture
def config_in_stdin(
    config_data: tuple[str, dict[str, Any]], monkeypatch: pytest.MonkeyPatch
) -> tuple[str, dict[str, Any]]:
    r"""A Cambiato configuration loaded into stdin.

    Returns
    -------
    config_data_str : str
        The configuration as a string of toml.

    config_exp : dict[str, Any]
        The expected configuration after loading and parsing `config_data_str`.
    """

    config_data_str, config_exp_original = config_data
    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = Path('-')

    monkeypatch.setattr(cambiato.config.config.sys, 'stdin', io.StringIO(config_data_str))

    return config_data_str, config_exp


@pytest.fixture
def empty_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    r"""A mocked stdin that is empty."""

    monkeypatch.setattr(cambiato.config.config.sys, 'stdin', io.StringIO(''))


@pytest.fixture
def config_file_from_config_env_var(
    config_data: tuple[str, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[Path, str, dict[str, Any]]:
    r"""The config file environment variable CAMBIATO_CONFIG_FILE is defined.

    The config file environment variable points to a Cambiato config file
    with a SQLite database.

    Returns
    -------
    config_file_path : pathlib.Path
        The path to the config file defined in the environment variable.

    config_data_str : str
        The configuration written to `config_file_path` as a string of toml.

    config_exp : dict[str, Any]
        The expected configuration after loading `config_file_path`.
    """

    config_data_str, config_exp_original = config_data

    config_file_path = tmp_path / 'Cambiato_from_env_var.toml'
    config_file_path.write_text(config_data_str)

    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = config_file_path

    monkeypatch.setenv(cambiato.config.config.CONFIG_FILE_ENV_VAR, str(config_file_path))

    return config_file_path, config_data_str, config_exp


@pytest.fixture
def config_file_from_default_location(
    config_data: tuple[str, dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> tuple[Path, str, dict[str, Any]]:
    r"""A config file at the default config file location of Cambiato.

    The true default config file location is "~/.config/Cambiato/Cambiato.toml".
    is mocked with a temporary directory.

    Returns
    -------
    config_file_path : pathlib.Path
        The path to the config file.

    config_data_str : str
        The configuration written to `config_file_path` as a string of toml.

    config_exp : dict[str, Any]
        The expected configuration after loading `config_file_path`.
    """

    config_data_str, config_exp_original = config_data

    config_file_path = tmp_path / 'Cambiato_from_default_location.toml'
    config_file_path.write_text(config_data_str)

    monkeypatch.setattr(cambiato.config.config, 'CONFIG_FILE_PATH', config_file_path)

    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = config_file_path

    return config_file_path, config_data_str, config_exp


@pytest.fixture
def default_config_file_location_does_not_exist(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> Path:
    r"""A mocked default config file location of Cambiato that does not exist.

    Returns
    -------
    config_file_path : pathlib.Path
        The path to the non-existing config file.
    """

    config_file_path = tmp_path / 'Cambiato_default_does_not_exist.toml'

    monkeypatch.setattr(cambiato.config.config, 'CONFIG_FILE_PATH', config_file_path)

    return config_file_path


@pytest.fixture
def config_file_with_syntax_error(tmp_path: Path) -> Path:
    r"""A Cambiato config file with syntax errors.

    Returns
    -------
    config_file_path : pathlib.Path
        The path to the config file with syntax errors.
    """

    source_filename = 'Cambiato_syntax_error.toml'
    source_config_file_path = STATIC_FILES_CONFIG_BASE_DIR / source_filename

    assert source_config_file_path.exists(), f'File "{source_config_file_path}" does not exist!'

    config_file_path = tmp_path / source_filename
    config_file_path.write_text(source_config_file_path.read_text())

    return config_file_path
