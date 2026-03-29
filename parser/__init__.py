"""
Парсер маршрутов Яндекс.Карт
"""
from .base import BaseParser
from .selenium_parser import SeleniumParser
from .requests_parser import RequestsParser
from .playwright_parser import PlaywrightParser


class YandexMapsParser:
    """
    Главный класс парсера Яндекс.Карт

    Пример использования:
        # С requests (быстро, но может сломаться при изменении структуры)
        parser = YandexMapsParser(backend='requests')
        route = parser.get_fastest_route(
            from_point="55.781939,37.864434",
            to_point="55.754025,37.617820",
            mode="auto"
        )

        # С selenium (надежно, но медленнее)
        parser = YandexMapsParser(backend='selenium', headless=True)
        route = parser.get_fastest_route(
            from_point="55.781939,37.864434",
            to_point="55.754025,37.617820"
        )
    """

    def __init__(self, backend='requests', **kwargs):
        """
        Инициализация парсера

        Args:
            backend: 'requests', 'selenium', или 'playwright'
            **kwargs: параметры для конкретного бэкенда
                - headless: bool (для selenium/playwright)
                - timeout: int (таймаут в секундах)
                - region: str (регион, по умолчанию '213')
                - city: str (город, по умолчанию 'moscow')
        """
        self.backend_name = backend
        self.kwargs = kwargs

        if backend == 'requests':
            self._parser = RequestsParser(**kwargs)
        elif backend == 'selenium':
            self._parser = SeleniumParser(**kwargs)
        elif backend == 'playwright':
            self._parser = PlaywrightParser(**kwargs)
        else:
            raise ValueError(f"Unknown backend: {backend}. Available: requests, selenium, playwright")

    def build_url(self, from_point, to_point, mode='auto', region=None, city=None):
        """Генерирует URL для маршрута"""
        return self._parser.build_url(from_point, to_point, mode, region, city)

    def build_url_by_coords(self, from_lat, from_lon, to_lat, to_lon, mode='auto'):
        """Генерирует URL по координатам"""
        return self._parser.build_url_by_coords(from_lat, from_lon, to_lat, to_lon, mode)

    def get_fastest_route(self, from_point, to_point, mode='auto', region=None, city=None):
        """
        Получает самый быстрый маршрут

        Args:
            from_point: Откуда (координаты "lat,lon" или название)
            to_point: Куда (координаты "lat,lon" или название)
            mode: Тип маршрута (auto, masstransit, pedestrian, bicycle, taxi)
            region: ID региона (по умолчанию 213 - Москва)
            city: Город (по умолчанию moscow)

        Returns:
            dict с данными маршрута
        """
        return self._parser.get_fastest_route(from_point, to_point, mode, region, city)

    def close(self):
        """Закрывает соединения (для selenium/playwright)"""
        if hasattr(self._parser, 'close'):
            self._parser.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# Создаем экземпляр по умолчанию для простого использования
default_parser = None


def get_parser(backend='requests', **kwargs):
    """Фабричная функция для получения парсера"""
    global default_parser
    if default_parser is None or default_parser.backend_name != backend:
        default_parser = YandexMapsParser(backend, **kwargs)
    return default_parser