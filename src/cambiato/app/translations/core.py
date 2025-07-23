r"""Core functionality to work with translations."""

# Standard library
from importlib.resources import files

# Local
from cambiato.app.translations.order import Order
from cambiato.config import Language
from cambiato.models.core import BaseModel


class TranslationModel(BaseModel):
    r"""The model of the translations.

    Parameters
    ----------
    order : cambiato.translations.Order
        The translations for the order page.
    """

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

    lang_file = files('cambiato.app.translations.translations').joinpath(f'{language}.json')

    return TranslationModel.model_validate_json(lang_file.read_text())
