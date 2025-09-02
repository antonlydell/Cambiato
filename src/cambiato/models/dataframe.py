r"""The DataFrame models, which represent table like structures of objects."""

# Standard library
from typing import ClassVar

# Local
from cambiato import exceptions
from cambiato.models.core import (
    ColumnList,
    IntIndexedDataFrameModel,
    StrIndexedDataFrameModel,
    StrMapping,
)


class ChecklistDataFrameModel(IntIndexedDataFrameModel):
    r"""A model of the checklists represented as a DataFrame."""

    c_checklist_id: ClassVar[str] = 'order_status_id'
    c_name: ClassVar[str] = 'name'

    dtypes: ClassVar[StrMapping] = {c_checklist_id: 'uint32[pyarrow]', c_name: 'string[pyarrow]'}
    index_cols: ClassVar[ColumnList] = [c_checklist_id]

    def display_row(self, id_: int | str) -> str:
        return self.df.loc[id_, self.c_name]  # type: ignore[return-value]


class FacilityDataFrameModel(IntIndexedDataFrameModel):
    r"""A model of the facilities represented as a DataFrame."""

    c_facility_id: ClassVar[str] = 'facility_id'
    c_ean: ClassVar[str] = 'ean'
    c_address: ClassVar[str] = 'address'

    dtypes: ClassVar[StrMapping] = {
        c_facility_id: 'uint32[pyarrow]',
        c_ean: 'uint64[pyarrow]',
        c_address: 'string[pyarrow]',
    }
    index_cols: ClassVar[ColumnList] = [c_facility_id]

    def display_row(self, id_: int | str) -> str:
        row = self.df.loc[id_, [self.c_ean, self.c_address]]  # type: ignore[list-item, index]

        return f'{row[self.c_ean]} | {row[self.c_address]}'


class OrderStatusDataFrameModel(IntIndexedDataFrameModel):
    r"""A model of the order statuses represented as a DataFrame."""

    c_order_status_id: ClassVar[str] = 'order_status_id'
    c_name: ClassVar[str] = 'name'

    dtypes: ClassVar[StrMapping] = {c_order_status_id: 'uint32[pyarrow]', c_name: 'string[pyarrow]'}
    index_cols: ClassVar[ColumnList] = [c_order_status_id]

    def display_row(self, id_: int | str) -> str:
        return self.df.loc[id_, self.c_name]  # type: ignore[return-value]


class OrderTypeDataFrameModel(IntIndexedDataFrameModel):
    r"""A model of the order types represented as a DataFrame."""

    c_order_type_id: ClassVar[str] = 'order_type_id'
    c_name: ClassVar[str] = 'name'

    dtypes: ClassVar[StrMapping] = {c_order_type_id: 'uint32[pyarrow]', c_name: 'string[pyarrow]'}
    index_cols: ClassVar[ColumnList] = [c_order_type_id]

    def display_row(self, id_: int | str) -> str:
        return self.df.loc[id_, self.c_name]  # type: ignore[return-value]


class UserDataFrameModel(StrIndexedDataFrameModel):
    r"""A model of the users represented as a DataFrame."""

    c_user_id: ClassVar[str] = 'user_id'
    c_displayname: ClassVar[str] = 'displayname'

    dtypes: ClassVar[StrMapping] = {c_user_id: 'string[pyarrow]', c_displayname: 'string[pyarrow]'}
    index_cols: ClassVar[ColumnList] = [c_user_id]

    def display_row(self, id_: int | str) -> str:
        return self.df.loc[id_, self.c_displayname]  # type: ignore[return-value]


class UtilityDataFrameModel(IntIndexedDataFrameModel):
    r"""A model of the utilities represented as a DataFrame."""

    c_utility_id: ClassVar[str] = 'utility_id'
    c_name: ClassVar[str] = 'name'

    dtypes: ClassVar[StrMapping] = {c_utility_id: 'uint32[pyarrow]', c_name: 'string[pyarrow]'}
    index_cols: ClassVar[ColumnList] = [c_utility_id]

    def display_row(self, id_: int | str) -> str:
        return self.df.loc[id_, self.c_name]  # type: ignore[return-value]
