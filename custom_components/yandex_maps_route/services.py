"""Сервисы для компонента."""
import voluptuous as vol
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_platform

from .const import DOMAIN

async def async_setup_services(hass: HomeAssistant) -> None:
    """Настройка сервисов."""
    
    async def async_update_route(call: ServiceCall) -> None:
        """Принудительное обновление маршрута."""
        entity_id = call.data.get("entity_id")
        # Логика обновления
        await hass.services.async_call(
            "homeassistant", "update_entity", {"entity_id": entity_id}
        )
    
    hass.services.async_register(
        DOMAIN, "update_route", async_update_route,
        schema=vol.Schema({
            vol.Required("entity_id"): str,
        })
    )