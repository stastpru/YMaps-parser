"""Сенсоры для отслеживания маршрута."""
from datetime import timedelta
import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.const import (
    ATTR_ATTRIBUTION,
    UnitOfLength,
    UnitOfTime,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
    UpdateFailed
)
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo

from .const import (
    DOMAIN, CONF_FROM_POINT, CONF_TO_POINT, CONF_MODE, 
    CONF_UPDATE_INTERVAL, DEVICE_MANUFACTURER, DEVICE_MODEL
)

from .parser import YandexMapsParser

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Настройка сенсоров через config entry."""
    coordinator = YandexMapsCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    
    # Создаем все сенсоры устройства
    sensors = [
        YandexMapsDistanceSensor(coordinator, entry),
        YandexMapsDurationSensor(coordinator, entry),
        YandexMapsDurationTextSensor(coordinator, entry),
        YandexMapsTrafficSensor(coordinator, entry),
        YandexMapsRouteTypeSensor(coordinator, entry),
        YandexMapsStatusSensor(coordinator, entry),
    ]
    
    async_add_entities(sensors, True)


class YandexMapsCoordinator(DataUpdateCoordinator):
    """Координатор для обновления данных маршрута."""
    
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Инициализация координатора."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"Yandex Maps Route {entry.entry_id}",
            update_interval=timedelta(seconds=entry.options.get(CONF_UPDATE_INTERVAL, 300)),
        )
        self.entry = entry
        self._parser = None
    
    def _get_parser(self):
        """Получение экземпляра парсера."""
        if self._parser is None:
            self._parser = YandexMapsParser(backend='requests', timeout=30)
        return self._parser
    
    async def _async_update_data(self):
        """Обновление данных маршрута."""
        try:
            return await self.hass.async_add_executor_job(self._update_route_data)
        except Exception as err:
            raise UpdateFailed(f"Ошибка обновления маршрута: {err}")
    
    def _update_route_data(self):
        """Синхронное обновление данных маршрута."""
        parser = self._get_parser()
        
        from_point = self.entry.data[CONF_FROM_POINT]
        to_point = self.entry.data[CONF_TO_POINT]
        mode = self.entry.data.get(CONF_MODE, 'auto')
        
        _LOGGER.debug(f"Обновление маршрута: {from_point} → {to_point} (mode: {mode})")
        
        route = parser.get_fastest_route(
            from_point=from_point,
            to_point=to_point,
            mode=mode
        )
        
        _LOGGER.debug(f"Полученные данные маршрута: {route}")
        
        # Нормализуем данные
        return {
            'success': route.get('success', False),
            'distance_km': route.get('distance_km', 0),
            'distance_meters': route.get('distance_meters', route.get('distance', 0)),
            'duration_minutes': route.get('duration_minutes', 0),
            'duration_seconds': route.get('duration_seconds', route.get('duration', 0)),
            'duration_text': route.get('duration_text', ''),
            'type': route.get('type', mode),
            'traffic_minutes': route.get('traffic_minutes'),
            'traffic_seconds': route.get('traffic_seconds'),
            'waypoints': route.get('waypoints', []),
        }


class BaseRouteSensor(CoordinatorEntity, SensorEntity):
    """Базовый класс для всех сенсоров маршрута с привязкой к устройству."""
    
    def __init__(self, coordinator: YandexMapsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator)
        self.entry = entry
        self._from_point = entry.data[CONF_FROM_POINT]
        self._to_point = entry.data[CONF_TO_POINT]
        
        # Привязываем к устройству
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=f"Маршрут: {self._from_point} → {self._to_point}",
            manufacturer=DEVICE_MANUFACTURER,
            model=DEVICE_MODEL,
            sw_version="1.0.0",
        )
    
    @property
    def extra_state_attributes(self):
        """Общие атрибуты для всех сенсоров."""
        if not self.coordinator.data:
            return {}
        
        return {
            ATTR_ATTRIBUTION: "Yandex Maps",
            "from_point": self._from_point,
            "to_point": self._to_point,
            "mode": self.entry.data.get(CONF_MODE, 'auto'),
            "last_update": self.coordinator.last_update_success,
        }


class YandexMapsDistanceSensor(BaseRouteSensor):
    """Сенсор расстояния."""
    
    def __init__(self, coordinator: YandexMapsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Расстояние"
        self._attr_unique_id = f"{entry.entry_id}_distance"
        self._attr_native_unit_of_measurement = UnitOfLength.KILOMETERS
        self._attr_icon = "mdi:map-marker-distance"
        self._attr_device_class = "distance"
    
    @property
    def native_value(self):
        if self.coordinator.data:
            return round(self.coordinator.data.get('distance_km', 0), 1)
        return None


class YandexMapsDurationSensor(BaseRouteSensor):
    """Сенсор времени в пути (минуты)."""
    
    def __init__(self, coordinator: YandexMapsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Время в пути"
        self._attr_unique_id = f"{entry.entry_id}_duration"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_icon = "mdi:clock-outline"
        self._attr_device_class = "duration"
    
    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get('duration_minutes', 0)
        return None


class YandexMapsDurationTextSensor(BaseRouteSensor):
    """Сенсор времени в пути (текстовый формат)."""
    
    def __init__(self, coordinator: YandexMapsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Время (текст)"
        self._attr_unique_id = f"{entry.entry_id}_duration_text"
        self._attr_icon = "mdi:clock"
    
    @property
    def native_value(self):
        if self.coordinator.data:
            return self.coordinator.data.get('duration_text', '')
        return None


class YandexMapsTrafficSensor(BaseRouteSensor):
    """Сенсор времени с учетом пробок."""
    
    def __init__(self, coordinator: YandexMapsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Время с пробками"
        self._attr_unique_id = f"{entry.entry_id}_traffic"
        self._attr_native_unit_of_measurement = UnitOfTime.MINUTES
        self._attr_icon = "mdi:traffic-light"
    
    @property
    def native_value(self):
        if self.coordinator.data and self.coordinator.data.get('traffic_minutes'):
            return self.coordinator.data.get('traffic_minutes')
        return None
    
    @property
    def available(self):
        """Доступен только если есть данные о пробках."""
        return super().available and self.native_value is not None


class YandexMapsRouteTypeSensor(BaseRouteSensor):
    """Сенсор типа маршрута."""
    
    def __init__(self, coordinator: YandexMapsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Тип маршрута"
        self._attr_unique_id = f"{entry.entry_id}_type"
        self._attr_icon = "mdi:car"
    
    @property
    def native_value(self):
        if self.coordinator.data:
            route_type = self.coordinator.data.get('type', 'unknown')
            types = {
                'auto': 'Автомобиль',
                'pedestrian': 'Пешком',
                'bike': 'Велосипед',
                'public-transport': 'Общественный транспорт',
                'masstransit': 'Общественный транспорт',
                'taxi': 'Такси'
            }
            return types.get(route_type, route_type)
        return None


class YandexMapsStatusSensor(BaseRouteSensor):
    """Сенсор статуса маршрута."""
    
    def __init__(self, coordinator: YandexMapsCoordinator, entry: ConfigEntry):
        super().__init__(coordinator, entry)
        self._attr_name = "Статус"
        self._attr_unique_id = f"{entry.entry_id}_status"
        self._attr_icon = "mdi:check-circle"
    
    @property
    def native_value(self):
        if self.coordinator.data:
            return "Успешно" if self.coordinator.data.get('success') else "Ошибка"
        return "Нет данных"
    
    @property
    def extra_state_attributes(self):
        attrs = super().extra_state_attributes
        if self.coordinator.data:
            attrs.update({
                "success": self.coordinator.data.get('success', False),
                "waypoints": self.coordinator.data.get('waypoints', []),
                "duration_seconds": self.coordinator.data.get('duration_seconds', 0),
                "distance_meters": self.coordinator.data.get('distance_meters', 0),
            })
        return attrs