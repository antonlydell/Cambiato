r"""Unit tests for the module config.config."""

# Standard library
from pathlib import Path
from typing import Any, ClassVar
from zoneinfo import ZoneInfo

# Third party
import pytest

# Local
from cambiato import exceptions
from cambiato.config import ConfigManager, load_config


class TestConfigManagerTimezone:
    r"""Tests for timezone field of `cambiato.config.ConfigManager`."""

    bwp: ClassVar[dict[str, str]] = {
        'public_key': 'bwp_public_key',
        'private_key': 'bwp_private_key',
    }

    default_tz: ClassVar[ZoneInfo] = ZoneInfo('Europe/Stockholm')

    def test_default_value(self) -> None:
        r"""Test the default value of the timezone field."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        cm = ConfigManager(bwp=self.bwp)

        # Verify
        # ===========================================================
        assert cm.timezone == self.default_tz

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        'timezone',
        [
            pytest.param(None, id='None'),
            pytest.param('', id='""'),
            pytest.param('    ', id='spaces'),
        ],
    )
    def test_empty_values(self, timezone: str | None) -> None:
        r"""Test empty values such as None and "", which should yield the default timezone."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        cm = ConfigManager(timezone=timezone, bwp=self.bwp)

        # Verify
        # ===========================================================
        assert cm.timezone == self.default_tz

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        ('timezone', 'exp_timezone'),
        [
            pytest.param('Europe/Berlin', ZoneInfo('Europe/Berlin'), id='str'),
            pytest.param(ZoneInfo('America/Denver'), ZoneInfo('America/Denver'), id='ZoneInfo'),
        ],
    )
    def test_valid_timezone(self, timezone: str | ZoneInfo, exp_timezone: ZoneInfo) -> None:
        r"""Test to supply a valid timezone."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        cm = ConfigManager(timezone=timezone, bwp=self.bwp)

        # Verify
        # ===========================================================
        assert cm.timezone == exp_timezone

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_timezone(self) -> None:
        r"""Test to to supply an invalid timezone."""

        # Setup
        # ===========================================================
        error_msg_exp = (
            'Failed to load timezone "invalid". Either the IANA timezone key is invalid '
            'or the system timezone database is missing. Install the tzdata package '
            'for your system or provide a valid timezone like "Europe/Stockholm".'
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.ConfigError) as exc_info:
            ConfigManager(timezone='invalid', bwp=self.bwp)

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_unsupported_type(self) -> None:
        r"""Test to to supply an unsupported type."""

        # Setup
        # ===========================================================
        error_msg_exp = 'Invalid timezone: "[]". Expected str or zoneinfo.ZoneInfo, got "list".'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.ConfigError) as exc_info:
            ConfigManager(timezone=[], bwp=self.bwp)

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================


class TestLoadConfig:
    r"""Tests for the function `cambiato.load_config`."""

    @pytest.mark.usefixtures(
        'config_in_stdin', 'config_file_from_config_env_var', 'config_file_from_default_location'
    )
    def test_load_from_config_file(self, config_file: tuple[Path, str, dict[str, Any]]) -> None:
        r"""Test to load the config from a direct path to a config file.

        The config is also present in:
        1. stdin,
        2. the config file environment variable,
        3. the default config file location.

        These locations should be ignored since supplying a direct path
        to a config file will take precedence over the other options.
        """

        # Setup
        # ===========================================================
        config_file_path, _, exp_result = config_file

        # Exercise
        # ===========================================================
        cm = load_config(path=config_file_path)

        # Verify
        # ===========================================================
        print(f'result\n{cm}\n')
        print(f'exp_result\n{exp_result}')

        assert cm.model_dump() == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.usefixtures('config_file_from_config_env_var', 'config_file_from_default_location')
    def test_load_from_stdin(self, config_in_stdin: tuple[str, dict[str, Any]]) -> None:
        r"""Test to load the config from stdin.

        The config is also present in:
        1. the config file environment variable,
        2. the default config file location.

        These locations should be ignored since stdin will take precedence over the other two.
        """

        # Setup
        # ===========================================================
        _, exp_result = config_in_stdin

        # Exercise
        # ===========================================================
        cm = load_config(path=Path('-'))

        # Verify
        # ===========================================================
        print(f'result\n{cm}\n')
        print(f'exp_result\n{exp_result}')

        assert cm.model_dump() == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.usefixtures(
        'remove_config_file_env_var', 'default_config_file_location_does_not_exist'
    )
    def test_path_is_none_and_config_in_stdin(
        self, config_in_stdin: tuple[str, dict[str, Any]]
    ) -> None:
        r"""Test to not specify a config file path while config exists in stdin.

        The config should be loaded from stdin.
        """

        # Setup
        # ===========================================================
        _, exp_result = config_in_stdin

        # Exercise
        # ===========================================================
        cm = load_config()

        # Verify
        # ===========================================================
        print(f'result\n{cm}\n')
        print(f'exp_result\n{exp_result}')

        assert cm.model_dump() == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.usefixtures('config_file_from_default_location')
    def test_load_from_config_file_env_var(
        self, config_file_from_config_env_var: tuple[Path, str, dict[str, Any]]
    ) -> None:
        r"""Test specifying the config file environment variable CAMBIATO_CONFIG_FILE.

        A config file in the default config file location is also present, but it
        should not be touched since the environment variable will take precedence.
        """

        # Setup
        # ===========================================================
        _, _, exp_result = config_file_from_config_env_var

        # Exercise
        # ===========================================================
        cm = load_config()

        # Verify
        # ===========================================================
        print(f'result\n{cm}\n')
        print(f'exp_result\n{exp_result}')

        assert cm.model_dump() == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.usefixtures('remove_config_file_env_var')
    def test_load_from_default_location(
        self, config_file_from_default_location: tuple[Path, str, dict[str, Any]]
    ) -> None:
        r"""Test to load the config from a config file in the default location.

        No other configuration sources are defined.
        """

        # Setup
        # ===========================================================
        _, _, exp_result = config_file_from_default_location

        # Exercise
        # ===========================================================
        cm = load_config()

        # Verify
        # ===========================================================
        print(f'result\n{cm}\n')
        print(f'exp_result\n{exp_result}')

        assert cm.model_dump() == exp_result

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    @pytest.mark.usefixtures(
        'remove_config_file_env_var', 'empty_stdin', 'default_config_file_location_does_not_exist'
    )
    def test_no_config_sources(self) -> None:
        r"""Test to load the configuration when no config sources exist."""

        # Setup
        # ===========================================================
        error_msg_exp = 'No configuration found! Check your sources!'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.ConfigError) as exc_info:
            load_config()

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg_exp == error_msg

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_from_config_file_is_dir(self, tmp_path: Path) -> None:
        r"""Test to load the config from a path that is a directory.

        `cambiato.exceptions.ConfigFileNotFoundError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        error_msg_exp = f'The config file "{tmp_path}" must be a file not a directory!'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.ConfigFileNotFoundError) as exc_info:
            load_config(path=tmp_path)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_from_config_file_does_not_exist(self, tmp_path: Path) -> None:
        r"""Test to load the config from a config file that does not exist.

        `cambiato.exceptions.ConfigFileNotFoundError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        config_file_path = tmp_path / 'does_not_exist.toml'
        error_msg_exp = f'The config file "{config_file_path}" does not exist!'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.ConfigFileNotFoundError) as exc_info:
            load_config(path=config_file_path)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_config_with_syntax_errors(self, config_file_with_syntax_error: Path) -> None:
        r"""Test to load a config file with syntax errors.

        `cambiato.exceptions.ParseConfigError` is expected to be raised.
        """

        # Setup
        # ===========================================================
        error_msg_exp = 'Syntax error in config :'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.ParseConfigError) as exc_info:
            load_config(path=config_file_with_syntax_error)

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert error_msg_exp in error_msg

        # Clean up - None
        # ===========================================================
