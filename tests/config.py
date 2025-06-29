r"""Configuration for the test suite of Cambiato."""

# Standard library
import os
import tomllib
from pathlib import Path
from typing import Any

# Third party
import pytest

# =============================================================================================
# Constants
# =============================================================================================

TEST_DIR = Path(__file__).parent
STATIC_FILES_BASE_DIR = TEST_DIR / 'static_files'
STATIC_FILES_CONFIG_BASE_DIR = STATIC_FILES_BASE_DIR / 'config'
TEST_SECRETS_FILE_ENV_VAR = 'CAMBIATO_SECRETS_FILE_TEST'


# =============================================================================================
# Secrets
# =============================================================================================


def load_secrets() -> tuple[dict[str, Any], str]:
    r"""Load the test secrets from the secrets' toml file.

    The path to the toml file should be specified in the
    environment variable "CAMBIATO_SECRETS_FILE_TEST".

    Returns
    -------
    secrets : dict[str, Any]
        The secrets loaded from the toml file. An empty dict is
        returned if no secrets could be loaded from the file.

    message : str
        A message if there was an error loading the test secrets.
        If no errors an empty string is returned.
    """

    secrets_file: Path | str | None = os.getenv(TEST_SECRETS_FILE_ENV_VAR)
    secrets: dict[str, Any] = {}

    if secrets_file is None:
        return secrets, f'Environment variable "{TEST_SECRETS_FILE_ENV_VAR}" is not set!'

    secrets_file = Path(secrets_file).expanduser()

    if secrets_file.is_dir():
        return secrets, f'"{secrets_file}" is a directory and not a file!'
    elif not secrets_file.exists():
        return secrets, f'"{secrets_file}" does not exist!'

    try:
        secrets = tomllib.loads(secrets_file.read_text())
    except (tomllib.TOMLDecodeError, TypeError) as e:
        return secrets, f'Syntax error in config : {e.args[0]}'

    return secrets, ''


secrets, message = load_secrets()

DB_URL_SECRETS_KEY = 'DB_URL'
DB_URL = secrets.get(DB_URL_SECRETS_KEY)

BWP_PUBLIC_KEY_SECRETS_KEY = 'bwp_public_key'
BWP_PUBLIC_KEY = secrets.get(BWP_PUBLIC_KEY_SECRETS_KEY)

BWP_PRIVATE_KEY_SECRETS_KEY = 'bwp_private_key'
BWP_PRIVATE_KEY = secrets.get(BWP_PRIVATE_KEY_SECRETS_KEY)

BWP_URL_SECRETS_KEY = 'bwp_url'
BWP_URL = secrets.get(BWP_URL_SECRETS_KEY)


# =============================================================================================
# Skip markers
# =============================================================================================

# Database
# ---------------------------------------------------------------------------------------------
can_run_db_integration_tests = DB_URL is not None

if message:
    db_integration_tests_skip_reason = (
        f'{message}\nSecrets missing: {DB_URL_SECRETS_KEY} = {DB_URL}'
    )
else:
    db_integration_tests_skip_reason = ''

db_integration_test_skipif = pytest.mark.skipif(
    not can_run_db_integration_tests, reason=db_integration_tests_skip_reason
)

# Bitwarden Passwordless.dev
# ---------------------------------------------------------------------------------------------
can_run_bwp_integration_tests = BWP_PUBLIC_KEY is not None and BWP_PRIVATE_KEY is not None

if message:
    bwp_integration_tests_skip_reason = (
        f'{message}\nSecrets missing:\n'
        f'{BWP_PUBLIC_KEY_SECRETS_KEY} = {BWP_PUBLIC_KEY}, '
        f'{BWP_PRIVATE_KEY_SECRETS_KEY} = {BWP_PRIVATE_KEY}'
    )
else:
    bwp_integration_tests_skip_reason = ''

bwp_integration_test_skipif = pytest.mark.skipif(
    not can_run_bwp_integration_tests, reason=bwp_integration_tests_skip_reason
)
