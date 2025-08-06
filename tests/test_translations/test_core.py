r"""Unit tests for the module translations.core."""

# Standard library
from typing import TypeAlias

# Third party
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

# Local
from cambiato.config import Language
from cambiato.translations.core import (
    TranslationModel,
    create_translation_mapping,
    load_translation,
    translate_dataframe,
)
from cambiato.translations.database import Translatable

TranslationMapping: TypeAlias = dict[int, dict[str, str]]


@pytest.fixture
def df_translation() -> tuple[pd.DataFrame, TranslationMapping, pd.DataFrame]:
    r"""A DataFrame with columns to translate.

    Returns
    -------
    df : pandas.DataFrame
        The DataFrame to translate.

    translation : dict[int, dict[str, str]]
        The translations for the columns of `df`.

    df_trans : pandas.DataFrame
        The translated DataFrame.
    """

    index = (1, 2)

    df = pd.DataFrame(
        index=index, data={'name': ['lumb', 'fally'], 'description': [None, 'Ciudad Blanca']}
    )

    translation = {
        1: {'name': 'Lumbridge', 'description': 'The town by the river'},
        2: {'name': 'Falador', 'description': 'The white city.'},
    }

    df_translated = pd.DataFrame(
        index=index,
        data={
            'name': ['Lumbridge', 'Falador'],
            'description': ['The town by the river', 'The white city.'],
        },
    )

    return df, translation, df_translated


class TestLoadTranslation:
    r"""Tests for the function `load_translation`."""

    @pytest.mark.parametrize('lang', [pytest.param(Language.EN, id='en')])
    def test_load_translation(self, lang: Language) -> None:
        r"""Test to load translations for the available languages.

        If a `TranslationModel` is returned without errors all required
        translations fields could be correctly read from the json file.
        """

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        trans = load_translation(language=lang)

        # Verify
        # ===========================================================
        assert isinstance(trans, TranslationModel)

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_invalid_language(self) -> None:
        r"""Test to load translations for a language that does not exist."""

        # Setup - None
        # ===========================================================

        # Exercise
        # ===========================================================
        with pytest.raises(FileNotFoundError) as exc_info:
            load_translation(language='invalid')  # type: ignore[arg-type]

        # Verify
        # ===========================================================
        error_msg = exc_info.exconly()
        print(error_msg)

        assert 'invalid.json' in error_msg

        # Clean up - None
        # ===========================================================


class TestCreateTranslationMapping:
    r"""Tests for the function `create_translation_mapping`."""

    def test_create_translation_mapping(self) -> None:
        r"""Test to create a translation mapping."""

        # Setup
        # ===========================================================
        translation = {
            1: Translatable(name='Lumbridge', description='The town by the river'),
            2: Translatable(name='Falador', description='The white city.'),
        }
        exp_result = {
            1: {'name': 'Lumbridge', 'description': 'The town by the river'},
            2: {'name': 'Falador', 'description': 'The white city.'},
        }

        # Exercise
        # ===========================================================
        result = create_translation_mapping(translation=translation)

        # Verify
        # ===========================================================
        assert result == exp_result

        # Clean up - None
        # ===========================================================


class TestTranslateDataFrame:
    r"""Tests for the function `translate_dataframe`."""

    def test_all_rows_of_df_have_translation_records(
        self, df_translation: tuple[pd.DataFrame, TranslationMapping, pd.DataFrame]
    ) -> None:
        r"""Test to translate a DataFrame where all rows have a translation record."""

        # Setup
        # ===========================================================
        df, translation, df_exp = df_translation

        # Exercise
        # ===========================================================
        df_result = translate_dataframe(df=df, translation=translation)

        # Verify
        # ===========================================================
        print(f'df_result:\n{df_result}\n')
        print(f'df_exp:\n{df_exp}')

        assert_frame_equal(df_result, df_exp)

        # Clean up - None
        # ===========================================================

    def test_some_rows_of_of_df_have_translation_records(
        self, df_translation: tuple[pd.DataFrame, TranslationMapping, pd.DataFrame]
    ) -> None:
        r"""Test to translate a DataFrame where some rows have a translation record."""

        # Setup
        # ===========================================================
        df, translation, df_trans = df_translation
        idx_1, idx_2 = df.index[0], df.index[1]

        df_exp = pd.concat([df.loc[[idx_1]], df_trans.loc[[idx_2]]], axis='index')

        # Exercise
        # ===========================================================
        df_result = translate_dataframe(
            df=df, translation={k: v for k, v in translation.items() if k == idx_2}
        )

        # Verify
        # ===========================================================
        print(f'df_result:\n{df_result}\n')
        print(f'df_exp:\n{df_exp}')

        assert_frame_equal(df_result, df_exp)

        # Clean up - None
        # ===========================================================

    def test_no_rows_of_dataframe_have_translation_records(
        self, df_translation: tuple[pd.DataFrame, TranslationMapping, pd.DataFrame]
    ) -> None:
        r"""Test to translate a DataFrame where no rows have a translation record.

        The input DataFrame should remain unchanged.
        """

        # Setup
        # ===========================================================
        df, _, _ = df_translation
        translation = {
            3: {'name': 'Lumbridge', 'description': 'The town by the river'},
            4: {'name': 'Falador', 'description': 'The white city.'},
        }

        # Exercise
        # ===========================================================
        df_result = translate_dataframe(df=df, translation=translation)

        # Verify
        # ===========================================================
        print(f'df_result:\n{df_result}\n')
        print(f'df_exp:\n{df}')

        assert_frame_equal(df_result, df)

        # Clean up - None
        # ===========================================================

    def test_filter_columns_to_translate(
        self, df_translation: tuple[pd.DataFrame, TranslationMapping, pd.DataFrame]
    ) -> None:
        r"""Test to only translate selected columns of the DataFrame."""

        # Setup
        # ===========================================================
        df, translation, df_trans = df_translation
        columns = [df.columns[0]]

        df_exp = pd.concat([df_trans[columns], df[df.columns[1]]], axis='columns')

        # Exercise
        # ===========================================================
        df_result = translate_dataframe(df=df, translation=translation, columns=columns)

        # Verify
        # ===========================================================
        print(f'df_result:\n{df_result}\n')
        print(f'df_exp:\n{df_exp}')

        assert_frame_equal(df_result, df_exp)

        # Clean up - None
        # ===========================================================
