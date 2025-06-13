r"""Fixtures for testing Cambiato."""

# Standard library
import io
from copy import deepcopy
from pathlib import Path
from typing import Any

# Third party
import pytest
from sqlalchemy import make_url

# Local
import cambiato.config
from cambiato.config import CONFIG_FILE_ENV_VAR
from tests.config import STATIC_FILES_CONFIG_BASE_DIR

type ConfigDict = dict[str, Any]


@pytest.fixture()
def remove_config_file_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    r"""Remove the config file environment variable CAMBIATO_CONFIG_FILE."""

    monkeypatch.delenv(CONFIG_FILE_ENV_VAR, raising=False)


@pytest.fixture()
def config_data(tmp_path: Path) -> tuple[str, dict[str, Any], Path]:
    r"""A Cambiato configuration with a SQLite database.

    Returns
    -------
    config_data_str : str
        The configuration as a string of toml.

    config_exp : dict[str, Any]
        The expected configuration after loading and parsing `config_data_str`.

    db_path : Path
        The full path to the SQLite database. The database does not exist.
    """

    source_filename = 'Cambiato.toml'
    source_config_file_path = STATIC_FILES_CONFIG_BASE_DIR / source_filename

    assert source_config_file_path.exists(), f'File "{source_config_file_path}" does not exist!'

    config_data_str = source_config_file_path.read_text()

    db_path = tmp_path / 'Cambiato.db'
    url = f'sqlite:///{str(db_path)}'

    config_data_str = config_data_str.replace(':url', url)

    database_config: ConfigDict = {
        'url': tuple(make_url(url)),
        'autoflush': False,
        'expire_on_commit': True,
        'create_database': True,
        'connect_args': {'timeout': 30},
        'engine_config': {'echo': True},
    }

    config_exp: ConfigDict = {'database': database_config}

    return config_data_str, config_exp, db_path


@pytest.fixture()
def config_file(
    config_data: tuple[str, dict[str, Any], Path], tmp_path: Path
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

    config_data_str, config_exp_original, _ = config_data

    config_file_path = tmp_path / 'Cambiato.toml'
    config_file_path.write_text(config_data_str)

    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = config_file_path

    return config_file_path, config_data_str, config_exp


@pytest.fixture()
def config_in_stdin(
    config_data: tuple[str, dict[str, Any], Path], monkeypatch: pytest.MonkeyPatch
) -> tuple[str, dict[str, Any], Path]:
    r"""A Cambiato configuration loaded into stdin.

    Returns
    -------
    config_data_str : str
        The configuration as a string of toml.

    config_exp : dict[str, Any]
        The expected configuration after loading and parsing `config_data_str`.

    db_path : Path
        The full path to the SQLite database.
    """

    config_data_str, config_exp_original, db_path = config_data
    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = Path('-')

    monkeypatch.setattr(cambiato.config.sys, 'stdin', io.StringIO(config_data_str))

    return config_data_str, config_exp, db_path


@pytest.fixture()
def config_file_from_config_env_var(
    config_data: tuple[str, dict[str, Any], Path],
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

    config_data_str, config_exp_original, _ = config_data

    config_file_path = tmp_path / 'Cambiato_from_env_var.toml'
    config_file_path.write_text(config_data_str)

    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = config_file_path

    monkeypatch.setenv(CONFIG_FILE_ENV_VAR, str(config_file_path))

    return config_file_path, config_data_str, config_exp


@pytest.fixture()
def config_file_from_default_location(
    config_data: tuple[str, dict[str, Any], Path],
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

    config_data_str, config_exp_original, _ = config_data

    config_file_path = tmp_path / 'Cambiato_from_default_location.toml'
    config_file_path.write_text(config_data_str)

    monkeypatch.setattr(cambiato.config, 'CONFIG_FILE_PATH', config_file_path)

    config_exp = deepcopy(config_exp_original)
    config_exp['config_file_path'] = config_file_path

    return config_file_path, config_data_str, config_exp


@pytest.fixture()
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
