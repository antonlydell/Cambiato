r"""Unit tests for the module translations.core."""

# Standard library
from collections.abc import Sequence
from typing import TypeAlias

# Third party
import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

# Local
from cambiato import exceptions
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

    df_translated : pandas.DataFrame
        The translated DataFrame.
    """

    index = (1, 2)

    df = pd.DataFrame(
        index=index, data={'name': ['lumb', 'fally'], 'description': [None, 'Ciudad Blanca']}
    )
    df.index.name = 'rs_id'

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
    df_translated.index.name = 'rs_id'

    return df, translation, df_translated


@pytest.fixture
def df_multi_translation() -> tuple[
    pd.DataFrame, tuple[TranslationMapping, TranslationMapping], pd.DataFrame
]:
    r"""A translated DataFrame with two translation mappings applied.

    Returns
    -------
    df : pandas.DataFrame
        The DataFrame to translate.

    translations : tuple[dict[int, dict[str, str]]
        The translations for the columns of `df`.

    df_translated : pandas.DataFrame
        The translated DataFrame.
    """

    index = (1, 2)

    df = pd.DataFrame(
        index=index,
        data={
            'name': ['lumb', 'fally'],
            'description': [None, 'Ciudad Blanca'],
            'tool_id': [8, 9],
            'tool': ['axe', 'tbox'],
        },
    )
    df.index.name = 'rs_id'

    name_desc_trans = {
        1: {'name': 'Lumbridge', 'description': 'The town by the river'},
        2: {'name': 'Falador', 'description': 'The white city.'},
    }
    tool_trans = {8: {'name': 'Axe'}, 9: {'name': 'Tinderbox'}}
    translations = (name_desc_trans, tool_trans)

    df_translated = pd.DataFrame(
        index=index,
        data={
            'name': ['Lumbridge', 'Falador'],
            'description': ['The town by the river', 'The white city.'],
            'tool_id': [8, 9],
            'tool': ['Axe', 'Tinderbox'],
        },
    )
    df_translated.index.name = 'rs_id'

    return df, translations, df_translated


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

    def test_some_rows_of_df_have_translation_records(
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
            df=df,
            translation={k: v for k, v in translation.items() if k == idx_2},
            columns=['name', 'description'],
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
        df_result = translate_dataframe(
            df=df, translation=translation, columns=('name', 'description')
        )

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

    def test_copy_df(
        self, df_translation: tuple[pd.DataFrame, TranslationMapping, pd.DataFrame]
    ) -> None:
        r"""Test to return a copy of the translated DataFrame rather than modifying inplace."""

        # Setup
        # ===========================================================
        df, translation, df_trans = df_translation

        # Exercise
        # ===========================================================
        df_result = translate_dataframe(df=df, translation=translation, copy=True)

        # Verify
        # ===========================================================
        print(f'df_result:\n{df_result}\n')
        print(f'df_exp:\n{df_trans}')

        assert_frame_equal(df_result, df_trans)

        with pytest.raises(AssertionError):  # df should not have been modified.
            assert_frame_equal(df_result, df)

        # Clean up - None
        # ===========================================================

    @pytest.mark.parametrize(
        ('columns', 'id_columns'),
        [
            pytest.param(
                (('name', 'description'), 'tool'),
                (None, 'tool_id'),
                id='all columns, default index col',
            ),
            pytest.param((None, ('tool',)), ('rs_id', 'tool_id'), id='None to specify all columns'),
        ],
    )
    def test_multi_translate(
        self,
        columns: Sequence[list[str] | str | None],
        id_columns: Sequence[str | None],
        df_multi_translation: tuple[
            pd.DataFrame, tuple[TranslationMapping, TranslationMapping], pd.DataFrame
        ],
    ) -> None:
        r"""Test to apply multiple translations to the selected columns of the same DataFrame."""

        # Setup
        # ===========================================================
        df, translations, df_trans = df_multi_translation

        # Exercise
        # ===========================================================
        df_result = translate_dataframe(
            df=df, translation=translations, columns=columns, id_column=id_columns
        )

        # Verify
        # ===========================================================
        print(f'df_result:\n{df_result}\n')
        print(f'df_exp:\n{df_trans}')

        assert_frame_equal(df_result, df_trans)

        # Clean up - None
        # ===========================================================

    @pytest.mark.raises
    def test_multi_translate_unequal_sequence_lengths(
        self,
        df_multi_translation: tuple[
            pd.DataFrame, tuple[TranslationMapping, TranslationMapping], pd.DataFrame
        ],
    ) -> None:
        r"""The length of the sequences translations, columns and id_column do not match."""

        # Setup
        # ===========================================================
        df, translations, _ = df_multi_translation
        error_msg_exp = 'Mismatch in lengths of translations, columns and id_column (2 != 3 != 1) !'

        # Exercise
        # ===========================================================
        with pytest.raises(exceptions.CambiatoError) as exc_info:
            translate_dataframe(
                df=df,
                translation=translations,
                columns=(['name', 'description'], 'tool', 'extra'),
                id_column=[None],
            )

        # Verify
        # ===========================================================
        error_msg = exc_info.value.args[0]
        print(error_msg)

        assert error_msg == error_msg_exp

        # Clean up - None
        # ===========================================================
