r"""Unit tests for the module `models.core`."""

# Standard library
from datetime import datetime
from typing import ClassVar

# Third party
import pandas as pd
import pytest
from pandas.testing import assert_series_equal

# Local
from cambiato import exceptions
from cambiato.models.core import ColumnList, IntIndexedDataFrameModel


class IntIndexedTestDataFrameModel(IntIndexedDataFrameModel):
    r"""An integer index DataFrame model to use for testing."""

    c_pk: ClassVar[str] = 'primary_key'
    c_name: ClassVar[str] = 'name'
    c_description: ClassVar[str] = 'description'
    c_created_at: ClassVar[str] = 'created_at'

    index_cols: ClassVar[ColumnList] = [c_pk]
    parse_dates: ClassVar[ColumnList] = [c_created_at]


@pytest.fixture
def int_indexed_df_model() -> IntIndexedTestDataFrameModel:
    r"""An integer index DataFrame model to use for testing.

    Returns
    -------
    IntIndexedTestDataFrameModel
        The model to test.
    """

    data = {
        1: {
            IntIndexedTestDataFrameModel.c_name: 'Electricity',
            IntIndexedTestDataFrameModel.c_description: 'The electricity utility.',
            IntIndexedTestDataFrameModel.c_created_at: datetime(2025, 8, 31, 13, 37),
        },
        2: {
            IntIndexedTestDataFrameModel.c_name: 'District Heating',
            IntIndexedTestDataFrameModel.c_description: 'The district heating utility.',
            IntIndexedTestDataFrameModel.c_created_at: datetime(2025, 8, 31, 13, 38),
        },
    }

    df = pd.DataFrame.from_dict(data, orient='index')
    df.index.name = IntIndexedTestDataFrameModel.c_pk

    return IntIndexedTestDataFrameModel(df=df)


class TestIntIndexedDataFrameModelGetIndex:
    r"""Tests for the method `IntIndexedDataFrameModel.get_index`."""

    def test_get_value_that_exists(
        self, int_indexed_df_model: IntIndexedTestDataFrameModel
    ) -> None:
        r"""Get the index value of a row where the selected column matches given value."""

        # Setup - None
        # ===========================================================

        # Exercise & Verify
        # ===========================================================
        assert int_indexed_df_model.get_index(value='Electricity', column='name') == 1

        # Clean up - None
        # ===========================================================

    def test_get_value_that_does_not_exists(
        self, int_indexed_df_model: IntIndexedTestDataFrameModel
    ) -> None:
        r"""Get the index value where the given value does not exist in selected column."""

        # Setup - None
        # ===========================================================

        # Exercise & Verify
        # ===========================================================
        assert int_indexed_df_model.get_index(value='does not exist', column='description') is None

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_column_not_part_of_dataframe(
        self, int_indexed_df_model: IntIndexedTestDataFrameModel
    ) -> None:
        r"""Test given column is not among the column names of the DataFrame."""

        # Setup
        # ===========================================================
        error_msg_exp = (
            'Column "does not exist" is not among the columns of '
            "the DataFrame : ['name', 'description', 'created_at']"
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.MissingColumnError) as exc_info:
            int_indexed_df_model.get_index(value='Electricity', column='does not exist')

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg == error_msg_exp

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_multiple_rows_match_column_value(
        self, int_indexed_df_model: IntIndexedTestDataFrameModel
    ) -> None:
        r"""Test to get the index value where given column value matches multiple rows."""

        # Setup
        # ===========================================================
        df = int_indexed_df_model.df
        c_name = int_indexed_df_model.c_name
        df.loc[2, c_name] = df.loc[1, c_name]

        error_msg_exp = 'Multiple rows match column "name" == \'Electricity\'!'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.MultipleRowsForColumnValueError) as exc_info:
            int_indexed_df_model.get_index(value='Electricity', column=c_name)

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg == error_msg_exp

        # Clean up - None
        # ===========================================================


class TestIntIndexedDataFrameModelGetIndexByRowNr:
    r"""Tests for the method `IntIndexedDataFrameModel.get_index_by_row_nr`."""

    def test_row_nr_that_exists(self, int_indexed_df_model: IntIndexedTestDataFrameModel) -> None:
        r"""Get the index of a row from its row number in the DataFrame."""

        # Setup - None
        # ===========================================================

        # Exercise & Verify
        # ===========================================================
        assert int_indexed_df_model.get_index_by_row_nr(row_nr=0) == 1

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_row_nr_that_does_not_exists(
        self, int_indexed_df_model: IntIndexedTestDataFrameModel
    ) -> None:
        r"""Get the index value from a row number that does not exist in the DataFrame."""

        # Setup
        # ===========================================================
        error_msg_exp = 'Row number 3 does not exist in DataFrame with nr_rows = 2!'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.MissingRowError) as exc_info:
            int_indexed_df_model.get_index_by_row_nr(3)

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg == error_msg_exp

        # Clean up - None
        # ===========================================================


class TestIntIndexedDataFrameModelGetColumn:
    r"""Tests for the method `IntIndexedDataFrameModel.get_column`."""

    def test_get_a_column_that_exists(
        self, int_indexed_df_model: IntIndexedTestDataFrameModel
    ) -> None:
        r"""Get a column from the DataFrame of the model."""

        # Setup
        # ===========================================================
        c_description = int_indexed_df_model.c_description
        s_exp = int_indexed_df_model.df[c_description]

        # Exercise
        # ===========================================================
        s_result = int_indexed_df_model.get_column(column=c_description)

        # Verify
        # ===========================================================
        assert_series_equal(s_result, s_exp)

        # Clean up - None
        # ===========================================================

    def test_get_unique_values(self, int_indexed_df_model: IntIndexedTestDataFrameModel) -> None:
        r"""Get the unique values of a column of the DataFrame."""

        # Setup
        # ===========================================================
        df = int_indexed_df_model.df
        df.loc[3, :] = df.loc[2, :]

        c_description = int_indexed_df_model.c_description
        s_exp = int_indexed_df_model.df.loc[1:2, c_description]

        # Exercise
        # ===========================================================
        s_result = int_indexed_df_model.get_column(column=c_description, unique=True)

        # Verify
        # ===========================================================
        assert_series_equal(s_result, s_exp)

        # Clean up - None
        # ===========================================================

    def test_sort_ascending(self, int_indexed_df_model: IntIndexedTestDataFrameModel) -> None:
        r"""Sort the extracted column in ascending order."""

        # Setup
        # ===========================================================
        c_name = int_indexed_df_model.c_name
        s_exp = int_indexed_df_model.df.loc[[2, 1], c_name]

        # Exercise
        # ===========================================================
        s_result = int_indexed_df_model.get_column(column=c_name, sort_ascending=True)

        # Verify
        # ===========================================================
        assert_series_equal(s_result, s_exp)

        # Clean up - None
        # ===========================================================

    def test_sort_descending(self, int_indexed_df_model: IntIndexedTestDataFrameModel) -> None:
        r"""Sort the extracted column in descending order."""

        # Setup
        # ===========================================================
        c_name = int_indexed_df_model.c_name
        s_exp = int_indexed_df_model.df.loc[:, c_name]

        # Exercise
        # ===========================================================
        s_result = int_indexed_df_model.get_column(column=c_name, sort_ascending=False)

        # Verify
        # ===========================================================
        assert_series_equal(s_result, s_exp)

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_column_not_part_of_dataframe(
        self, int_indexed_df_model: IntIndexedTestDataFrameModel
    ) -> None:
        r"""Get a column that does not exist in the DataFrame of the model."""

        # Setup
        # ===========================================================
        error_msg_exp = (
            'Column "does not exist" is not among the columns of '
            "the DataFrame : ['name', 'description', 'created_at']"
        )

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.MissingColumnError) as exc_info:
            int_indexed_df_model.get_column(column='does not exist')

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg == error_msg_exp

        # Clean up - None
        # ===========================================================
