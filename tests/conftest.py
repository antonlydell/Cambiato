r"""Fixtures for testing Cambiato."""

# Standard library
import io
from copy import deepcopy
from pathlib import Path
from typing import Any

# Third party
import pytest
from pydantic import AnyHttpUrl
from sqlalchemy import URL, make_url

# Local
import cambiato.config
from cambiato.config import BITWARDEN_PASSWORDLESS_API_URL, CONFIG_FILE_ENV_VAR, Language
from tests.config import (
    BWP_PRIVATE_KEY,
    BWP_PUBLIC_KEY,
    BWP_URL,
    DB_URL,
    STATIC_FILES_CONFIG_BASE_DIR,
)

type ConfigDict = dict[str, Any]


@pytest.fixture(scope='session')
def db_url() -> tuple[str, URL]:
    r"""The url to the test database.

    If the URL cannot be loaded from the test configuration of `DB_URL`
    a syntactically valid dummy URL to the database is provided.

    Returns
    -------
    url_str : str
        A string version of the database url.

    url : sqlalchemy.URL
        A SQLAlchemy URL of `url_str`.
    """

    url_str = 'postgresql+psycopg2://user:pw@myserver:5432/postgresdb' if DB_URL is None else DB_URL

    return url_str, make_url(url_str)


@pytest.fixture(scope='session')
def bwp_public_key() -> str:
    r"""The public key to the test instance of Bitwarden Passwordless.dev.

    If the public key cannot be loaded from the test configuration
    of `BWP_PUBLIC_KEY` a dummy key is provided.

    Returns
    -------
    str
        The public key to the test instance of Bitwarden Passwordless.dev.
    """

    return 'bwp_public_key' if BWP_PUBLIC_KEY is None else BWP_PUBLIC_KEY


@pytest.fixture(scope='session')
def bwp_private_key() -> str:
    r"""The private key to the test instance of Bitwarden Passwordless.dev.

    If the private key cannot be loaded from the test configuration
    of `BWP_PRIVATE_KEY` a dummy key is provided.

    Returns
    -------
    str
        The private key to the test instance of Bitwarden Passwordless.dev.
    """

    return 'bwp_private_key' if BWP_PRIVATE_KEY is None else BWP_PRIVATE_KEY


@pytest.fixture(scope='session')
def bwp_url() -> tuple[str, AnyHttpUrl]:
    r"""The base url to the Bitwarden Passwordless.dev backend API.

    If the url cannot be loaded from the test configuration
    of `BWP_URL` the default url of Bitwarden Passwordless.dev is used.

    Returns
    -------
    url_str : str
        A string version of the API url.

    url : pydantic.AnyHttpUrl
        The pydantic URL of `url_str`.
    """

    if BWP_URL is None:
        url_str = str(BITWARDEN_PASSWORDLESS_API_URL)
        url = BITWARDEN_PASSWORDLESS_API_URL
    else:
        url_str = BWP_URL
        url = AnyHttpUrl(BWP_URL)

    return url_str, url


@pytest.fixture
def remove_config_file_env_var(monkeypatch: pytest.MonkeyPatch) -> None:
    r"""Remove the config file environment variable CAMBIATO_CONFIG_FILE."""

    monkeypatch.delenv(CONFIG_FILE_ENV_VAR, raising=False)


@pytest.fixture
def config_data(
    db_url: tuple[str, URL],
    bwp_public_key: str,
    bwp_private_key: str,
    bwp_url: tuple[str, AnyHttpUrl],
) -> tuple[str, dict[str, Any]]:
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

    db_url_str, db_url_sqlalchemy = db_url
    bwp_url_str, bwp_url_pydantic = bwp_url

    config_data_str = (
        config_data_str.replace(':db_url', db_url_str)
        .replace(':bwp_public_key', bwp_public_key)
        .replace(':bwp_private_key', bwp_private_key)
        .replace(':bwp_url', bwp_url_str)
    )

    database_config: ConfigDict = {
        'url': tuple(db_url_sqlalchemy),
        'autoflush': False,
        'expire_on_commit': True,
        'create_database': True,
        'connect_args': {'timeout': 30},
        'engine_config': {'echo': True},
    }

    bwp_config: ConfigDict = {
        'public_key': bwp_public_key,
        'private_key': bwp_private_key,
        'url': bwp_url_pydantic,
    }

    config_exp: ConfigDict = {
        'language': Language.EN,
        'database': database_config,
        'bwp': bwp_config,
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

    monkeypatch.setattr(cambiato.config.sys, 'stdin', io.StringIO(config_data_str))

    return config_data_str, config_exp


@pytest.fixture
def empty_stdin(monkeypatch: pytest.MonkeyPatch) -> None:
    r"""A mocked stdin that is empty."""

    monkeypatch.setattr(cambiato.config.sys, 'stdin', io.StringIO(''))


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

    monkeypatch.setenv(CONFIG_FILE_ENV_VAR, str(config_file_path))

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

    monkeypatch.setattr(cambiato.config, 'CONFIG_FILE_PATH', config_file_path)

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

    monkeypatch.setattr(cambiato.config, 'CONFIG_FILE_PATH', config_file_path)

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
