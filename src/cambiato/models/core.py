r"""The core data models of Cambiato."""

# Standard library
from collections.abc import Mapping
from typing import Any, ClassVar, TypeAlias

# Third party
import pandas as pd
from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, Field, ValidationError

# Local
from cambiato import exceptions

StrMapping: TypeAlias = Mapping[str, str]
ColumnList: TypeAlias = list[str]


class BaseModel(PydanticBaseModel):
    r"""The BaseModel that all models inherit from."""

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True, frozen=True)

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        try:
            super().__init__(**kwargs)
        except ValidationError as e:
            raise exceptions.CambiatoError(str(e)) from None


class BaseDataFrameModel(BaseModel):
    """The base model that all DataFrame models will inherit from.

    A DataFrame model represents a database table, a query or some other table like structure.
    using a :class:`pandas.DataFrame`. The DataFrame is accessible from the `df` attribute.
    Each column name of the DataFrame should be implemented as a class variable starting with
    the prefix "c_", e.g. `c_name: ClassVar[str] = 'name'` for a name column. The class variables
    listed below should be defined for each subclass of this model.

    Class Variables
    ---------------
    dtypes : ClassVar[dict[str, str]]
        The mapping of column names to their datatypes of the DataFrame.

    index_cols : ClassVar[list[str]]
        The index columns of the DataFrame.

    parse_dates : ClassVar[list[str]]
        The columns of the DataFrame that should be parsed into datetime columns.

    Parameters
    ----------
    df : pandas.DataFrame, default pandas.DataFrame()
        The contents of the model as a DataFrame.
    """

    dtypes: ClassVar[StrMapping] = {}
    index_cols: ClassVar[ColumnList] = []
    parse_dates: ClassVar[ColumnList] = []

    df: pd.DataFrame = Field(default_factory=pd.DataFrame)

    @property
    def shape(self) -> tuple[int, int]:
        r"""The shape (rows, cols) of the DataFrame."""

        return self.df.shape

    @property
    def index(self) -> pd.Index:
        r"""The index column(s) of the DataFrame."""

        return self.df.index

    @property
    def row_count(self) -> int:
        r"""The number of rows of the DataFrame."""

        return self.df.shape[0]

    @property
    def empty(self) -> bool:
        r"""Check if the DataFrame is empty or not."""

        return self.row_count == 0

    @property
    def col_dtypes(self) -> pd.Series:
        r"""The dtypes of the columns of the DataFrame `df`."""

        return self.df.dtypes

    def display_row(self, id_: int | str) -> str:
        r"""String representation of a row in the DataFrame.

        Each subclass should override this method to fit its DataFrame content.

        Parameters
        ----------
        id_: int or str
            The index ID of the DataFrame for which to retrieve a row.

        Returns
        -------
        str
            The string representation of the row.
        """

        return str(id_)
