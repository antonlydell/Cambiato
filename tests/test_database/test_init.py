r"""Unit tests for module `database.init`"""

# Standard library
from pathlib import Path

# Third party
import pytest
from sqlalchemy import func, select, text
from sqlalchemy.exc import IntegrityError

# Local
from cambiato.database import create_session_factory, init, models

# =============================================================================================
# Tests
# =============================================================================================


class TestInit:
    r"""Tests for the function `init`."""

    def test_initialize_sqlite_database(self, tmp_path: Path) -> None:
        r"""Test to initialize a SQLite database."""

        # Setup
        # ===========================================================
        db = tmp_path / 'Cambiato.db'
        url = f'sqlite:///{db!s}'
        session_factory = create_session_factory(url=url, create_database=True)

        get_tables_query = text("SELECT name FROM sqlite_master WHERE type = 'table'")
        tables_exp = {
            t.__tablename__
            for m in models.__dict__
            if hasattr(t := getattr(models, m), '__tablename__')
        }

        # Tables with default records.
        queries = {
            'DType': select(func.count()).select_from(models.DType),
            'Unit': select(func.count()).select_from(models.Unit),
            'ValueColumnName': select(func.count()).select_from(models.ValueColumnName),
            'Utility': select(func.count()).select_from(models.Utility),
            'CoordinateSystem': select(func.count()).select_from(models.CoordinateSystem),
            'KeyType': select(func.count()).select_from(models.KeyType),
            'LocationType': select(func.count()).select_from(models.LocationType),
            'CustomerType': select(func.count()).select_from(models.CustomerType),
            'ContactMethod': select(func.count()).select_from(models.ContactMethod),
            'PhoneType': select(func.count()).select_from(models.PhoneType),
            'DeviceType': select(func.count()).select_from(models.DeviceType),
            'DeviceState': select(func.count()).select_from(models.DeviceState),
            'DeviceLocationType': select(func.count()).select_from(models.DeviceLocationType),
            'FacilityAccessMethod': select(func.count()).select_from(models.FacilityAccessMethod),
            'MountType': select(func.count()).select_from(models.MountType),
            'OrderType': select(func.count()).select_from(models.OrderType),
            'OrderStatus': select(func.count()).select_from(models.OrderStatus),
        }

        # Exercise
        # ===========================================================
        with session_factory() as session:
            init(session=session)

        # Verify
        # ===========================================================
        with session_factory() as session:
            tables = {t for t in session.scalars(get_tables_query)}  # noqa: C416

            for table, query in queries.items():
                count = session.scalars(query).one()

                assert count > 0, f'{table} : Records not created!'

        # Not all expected tables have been created.
        diff_in_tables_exp_not_in_tables = tables_exp.difference(tables)
        print(f'{diff_in_tables_exp_not_in_tables=}')

        assert not diff_in_tables_exp_not_in_tables, 'diff_in_tables_exp_not_in_tables'

        # All other tables than the expected ones should belong to streamlit_passwordless.
        diff_in_tables_not_in_tables_exp = tables.difference(tables_exp)
        print(f'{diff_in_tables_not_in_tables_exp=}')

        for table in diff_in_tables_not_in_tables_exp:
            assert table.startswith('stp_'), f'{table=} is not a streamlit_passwordless table!'

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_sqlite_foreign_key_constraints_enabled(self) -> None:
        r"""Test that foreign key constraints are enabled in a SQLite database."""

        # Setup
        # ===========================================================
        session_factory = create_session_factory(url='sqlite://', create_database=True)

        # Exercise
        # ===========================================================
        with session_factory() as session:
            session.add(models.ElectricityMeter(device_id=1))
            with pytest.raises(IntegrityError) as exc_info:
                session.commit()

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'FOREIGN KEY constraint failed' in error_msg

        # Clean up - None
        # ===========================================================
