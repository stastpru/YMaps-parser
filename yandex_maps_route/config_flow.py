"""Config flow для Yandex Maps Route."""
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import (
    DOMAIN, CONF_FROM_POINT, CONF_TO_POINT, CONF_MODE, 
    CONF_UPDATE_INTERVAL, DEFAULT_MODE, 
    DEFAULT_UPDATE_INTERVAL, MODES
)

class YandexMapsRouteConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow для компонента."""
    
    VERSION = 1
    
    async def async_step_user(self, user_input=None):
        """Первый шаг настройки."""
        errors = {}
        
        if user_input is not None:
            if not user_input[CONF_FROM_POINT] or not user_input[CONF_TO_POINT]:
                errors["base"] = "empty_points"
            else:
                return self.async_create_entry(
                    title=f"Маршрут: {user_input[CONF_FROM_POINT]} → {user_input[CONF_TO_POINT]}",
                    data=user_input,
                )
        
        data_schema = vol.Schema({
            vol.Required(CONF_FROM_POINT): str,
            vol.Required(CONF_TO_POINT): str,
            vol.Optional(CONF_MODE, default=DEFAULT_MODE): vol.In(MODES),
            vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): int,
        })
        
        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
    
    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Возвращает options flow."""
        return YandexMapsRouteOptionsFlow(config_entry)


class YandexMapsRouteOptionsFlow(config_entries.OptionsFlow):
    """Options flow для компонента."""
    
    def __init__(self, config_entry):
        """Инициализация - НЕ присваиваем config_entry как атрибут!"""
        self._config_entry = config_entry  # Используем protected атрибут
    
    async def async_step_init(self, user_input=None):
        """Обработка опций."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        
        options_schema = vol.Schema({
            vol.Required(
                CONF_UPDATE_INTERVAL,
                default=self._config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
            ): int,
        })
        
        return self.async_show_form(
            step_id="init",
            data_schema=options_schema,
        )