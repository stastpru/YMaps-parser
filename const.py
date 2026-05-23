"""Константы для компонента."""
DOMAIN = "yandex_maps_route"
DEFAULT_NAME = "Yandex Maps Route"

CONF_FROM_POINT = "from_point"
CONF_TO_POINT = "to_point"
CONF_MODE = "mode"
CONF_BACKEND = "backend"
CONF_UPDATE_INTERVAL = "update_interval"

DEFAULT_MODE = "auto"
DEFAULT_UPDATE_INTERVAL = 300

MODES = ["auto", "pedestrian", "bike", "public-transport"]