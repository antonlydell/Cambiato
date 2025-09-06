r"""The core component that includes all component translation models."""

# Local
from cambiato.models.core import BaseModel

from .dataframes import DataFrames


class Components(BaseModel):
    r"""The translations of the components."""

    dataframes: DataFrames
