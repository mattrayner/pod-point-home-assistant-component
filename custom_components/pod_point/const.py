"""Constants for integration_blueprint."""
# Base component constants
NAME = "Pod Point"
DOMAIN = "pod_point"
DOMAIN_DATA = f"{DOMAIN}_data"
VERSION = "0.0.1"
ATTRIBUTION = "Data provided by https://pod-point.com/"
ISSUE_URL = "https://github.com/mattrayner/pod-point-home-assistant-component/issues"

# Icons
ICON = "mdi:ev-plug-type2"
SWITCH_ICON = "mdi:ev-station"

# Device classes
BINARY_SENSOR_DEVICE_CLASS = "plug"

# Platforms
BINARY_SENSOR = "binary_sensor"
SENSOR = "sensor"
SWITCH = "switch"
PLATFORMS = [BINARY_SENSOR, SENSOR, SWITCH]

# Configuration and options
CONF_ENABLED = "enabled"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"

# Defaults
DEFAULT_NAME = DOMAIN

# State attributes
ATTR_ID = "pod_id"
ATTR_PSL = "psl"
ATTR_HOME = "home"
ATTR_PAYG = "payg"
ATTR_PUBLIC = "public"
ATTR_EVZONE = "ev_zone"
ATTR_LAT = "lat"
ATTR_LNG = "lng"
ATTR_UNIT_ID = "unit_id"
ATTR_COMMISSIONED = "date_commissioned"
ATTR_CREATED = "date_created"
ATTR_LAST_CONTACT = "last_contacted_at"
ATTR_CONTACTLESS_ENABLED = "contactless_enabled"
ATTR_TIMEZONE = "timezone"
ATTR_MODEL = "model"
ATTR_PRICE = "price"
ATTR_STATUS = "status"
ATTR_STATUS_KEY_NAME = "key_name"
ATTR_STATUS_NAME = "name"
ATTR_STATUS_LABEL = "label"
ATTR_STATUS_DOOR = "door"
ATTR_STATUS_DOOR_ID = "door_id"
ATTR_CONNECTOR = "connector"
ATTR_CONNECTOR_ID = "id"
ATTR_CONNECTOR_DOOR = "door"
ATTR_CONNECTOR_DOOR_ID = "door_id"
ATTR_CONNECTOR_POWER = "power"
ATTR_CONNECTOR_CURRENT = "current"
ATTR_CONNECTOR_VOLTAGE = "voltage"
ATTR_CONNECTOR_CHARGE_METHOD = "charge_method"
ATTR_CONNECTOR_HAS_CABLE = "has_cable"
ATTR_CONNECTOR_SOCKET = "socket"
ATTR_CONNECTOR_SOCKET_TYPE = "type"
ATTR_CONNECTOR_SOCKET_OCPP_NAME = "ocpp_name"
ATTR_CONNECTOR_SOCKET_OCPP_CODE = "ocpp_code"
ATTR_STATE = "state"

ATTR_STATE_AVAILABLE = "available"
ATTR_STATE_UNAVAILABLE = "unavailable"
ATTR_STATE_CHARGING = "charging"
ATTR_STATE_OUT_OF_SERVICE = "out-of-service"
ATTR_STATE_WAITING = "waiting-for-schedule"
ATTR_STATE_RANKING = [
    ATTR_STATE_AVAILABLE,
    ATTR_STATE_UNAVAILABLE,
    ATTR_STATE_CHARGING,
    ATTR_STATE_OUT_OF_SERVICE,
]

# Flags
CHARGING_FLAG = ATTR_STATE_CHARGING

# API Details
BASE_API_VERSION = "v4"
BASE_API_URL = "https://api.pod-point.com/" + BASE_API_VERSION

STARTUP_MESSAGE = f"""
-------------------------------------------------------------------
{NAME}
Version: {VERSION}
This is a custom integration!
If you have any issues with this you need to open an issue here:
{ISSUE_URL}
-------------------------------------------------------------------
"""
