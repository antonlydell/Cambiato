r"""The database tables."""

# Third party
from streamlit_passwordless.database.models import CustomRole, Email, Role, User, UserSignIn

# Local
from .core import (
    SCHEMA,
    Base,
    CoordinateSystem,
    DType,
    Key,
    KeyType,
    ManufactureBatch,
    Manufacturer,
    ObjectType,
    TypeDescription,
    Unit,
    Utility,
    ValueColumnName,
)
from .default import add_default_models_to_session
from .relations import (
    Checklist,
    ChecklistItem,
    ContactMethod,
    Customer,
    CustomerEmail,
    CustomerPhone,
    CustomerType,
    Device,
    DeviceFacilityEnabledDisabledLog,
    DeviceFacilityLink,
    DeviceLocationType,
    DeviceState,
    DeviceType,
    DistrictHeatingCoolingFacility,
    ElectricityFacility,
    ElectricityMeter,
    Facility,
    FacilityAccessMethod,
    Image,
    LatestDeviceMeterReading,
    Location,
    LocationType,
    MountType,
    Order,
    OrderChecklistItem,
    OrderComment,
    OrderEnabledDisabledDevice,
    OrderEnabledDisabledDeviceMR,
    OrderScheduleLog,
    OrderStatus,
    OrderType,
    PhoneType,
)

# The Public API
__all__ = [
    # core
    'SCHEMA',
    'Base',
    'CoordinateSystem',
    'DType',
    'Key',
    'KeyType',
    'ManufactureBatch',
    'Manufacturer',
    'ObjectType',
    'TypeDescription',
    'Unit',
    'Utility',
    'ValueColumnName',
    # default
    'add_default_models_to_session',
    # relations
    'Checklist',
    'ChecklistItem',
    'ContactMethod',
    'Customer',
    'CustomerEmail',
    'CustomerPhone',
    'CustomerType',
    'Device',
    'DeviceFacilityEnabledDisabledLog',
    'DeviceFacilityLink',
    'DeviceLocationType',
    'DeviceState',
    'DeviceType',
    'DistrictHeatingCoolingFacility',
    'ElectricityFacility',
    'ElectricityMeter',
    'Facility',
    'FacilityAccessMethod',
    'Image',
    'LatestDeviceMeterReading',
    'Location',
    'LocationType',
    'MountType',
    'Order',
    'OrderChecklistItem',
    'OrderComment',
    'OrderEnabledDisabledDevice',
    'OrderEnabledDisabledDeviceMR',
    'OrderScheduleLog',
    'OrderStatus',
    'OrderType',
    'PhoneType',
    # streamlit-passwordless
    'CustomRole',
    'Email',
    'Role',
    'User',
    'UserSignIn',
]
