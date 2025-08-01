r"""Core functionality to work with translations."""

# Standard library
from importlib.resources import files

# Local
from cambiato.config import Language
from cambiato.models.core import BaseModel
from cambiato.translations.database import Database
from cambiato.translations.order import Order


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
