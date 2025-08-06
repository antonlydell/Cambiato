r"""Core functionality to work with translations."""

# Standard library
from collections.abc import Mapping
from contextlib import suppress
from importlib.resources import files
from typing import Any, Protocol, TypeAlias, TypeVar

# Third party
import pandas as pd

# Local
from cambiato.config import Language
from cambiato.models.core import BaseModel
from cambiato.translations.database import Database
from cambiato.translations.order import Order

_Translated: TypeAlias = str | Mapping[str, str]
TranslationMapping: TypeAlias = Mapping[int, _Translated] | Mapping[str, _Translated]


class SupportsModelDump(Protocol):
    r"""Implements the `model_dump` method."""

    def model_dump(self) -> dict[str, Any]: ...


T = TypeVar('T', bound=SupportsModelDump)


class TranslationModel(BaseModel):
    r"""The model of the translations.

    Parameters
    ----------
    database : cambiato.translations.Database
        The translations for the default data in the database.

    order : cambiato.translations.Order
        The translations for the order page.
    """

    database: Database
    order: Order


def load_translation(language: Language) -> TranslationModel:
    r"""Load the translations for the selected language.

    Parameters
    ----------
    language : cambiato.config.Language
        The translation language to load.

    Returns
    -------
    cambiato.app.translations.TranslationModel
        The model of the translations for the application.
    """

    lang_file = files('cambiato.translations.translations').joinpath(f'{language}.json')

    return TranslationModel.model_validate_json(lang_file.read_text())


def create_translation_mapping(translation: Mapping[int, T]) -> TranslationMapping:
    r"""Create a translation mapping to use for translating a DataFrame.

    Parameters
    ----------
    translation : Mapping[int, T]
        A mapping of ID:s (usually primary keys) to objects that implement the method:
        `model_dump() -> dict[str, Any]`.

    Returns
    -------
    cambiato.translations.TranslationMapping
        The translations for each ID defined as the keys in `translation`.
    """

    return {key: value.model_dump() for key, value in translation.items()}


def translate_dataframe(
    df: pd.DataFrame, translation: TranslationMapping, columns: list[str] | None = None
) -> pd.DataFrame:
    r"""Translate selected columns of a :class:`pandas.DataFrame`.

    Parameters
    ----------
    df : pandas.DataFrame
        The DataFrame to in which to translate columns.

    translation : cambiato.translations.TranslationMapping
        The translations for the columns of `df`. The keys should match the index of `df`.

    columns : list[str] or None default None
        The columns of `df` to translate. The supplied columns should be found in both `df`
        and `translation`. If None all columns are translated.

    Returns
    -------
    df : pandas.DataFrame
        An updated version of `df` with selected columns translated.
    """

    df_trans = pd.DataFrame(
        index=translation.keys(),  # type: ignore[call-overload]
        data=translation.values(),
        columns=columns,
    )
    with suppress(KeyError):  # KeyError if no values to translate were found in df.
        if columns:
            df.loc[df_trans.index, columns] = df_trans[columns]
        else:
            df.loc[df_trans.index, :] = df_trans

    return df
