"""Базовый класс для всех парсеров"""
from abc import ABC, abstractmethod
import json
import re


class BaseParser(ABC):
    """Абстрактный базовый класс парсера"""

    def __init__(self, timeout=30, region='213', city='moscow', **kwargs):
        self.timeout = timeout
        self.region = region
        self.city = city
        self.kwargs = kwargs

    def build_url(self, from_point, to_point, mode='auto', region=None, city=None):
        """
        Генерирует URL для маршрута

        Args:
            from_point: Откуда (координаты "lat,lon" или название)
            to_point: Куда (координаты "lat,lon" или название)
            mode: Тип маршрута (auto, masstransit, pedestrian, bicycle, taxi)
            region: ID региона (по умолчанию 213 - Москва)
            city: Город (по умолчанию moscow)

        Returns:
            str: URL
        """
        region = region or self.region
        city = city or self.city

        base_url = f"https://yandex.ru/maps/{region}/{city}/"

        # Обрабатываем точки
        if ',' in str(from_point) and isinstance(from_point, str):
            from_coords = from_point.replace(',', '%2C')
        else:
            from_coords = from_point

        if ',' in str(to_point) and isinstance(to_point, str):
            to_coords = to_point.replace(',', '%2C')
        else:
            to_coords = to_point

        params = {
            'mode': 'routes',
            'rtext': f"{from_coords}~{to_coords}",
            'rtt': mode,
            'z': '13'
        }

        param_str = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{param_str}"

    def build_url_by_coords(self, from_lat, from_lon, to_lat, to_lon, mode='auto'):
        """Генерирует URL по координатам"""
        return self.build_url(f"{from_lat},{from_lon}", f"{to_lat},{to_lon}", mode)

    @abstractmethod
    def get_fastest_route(self, from_point, to_point, mode='auto', region=None, city=None):
        """Получает самый быстрый маршрут - должен быть реализован в наследниках"""
        pass

    def _extract_route_from_html(self, html):
        """
        Извлекает данные маршрута из HTML

        Args:
            html: HTML страницы

        Returns:
            dict: Данные маршрута или None
        """
        # Ищем JSON с данными
        match = re.search(r'<script class="state-view" type="application/json">(.*?)</script>', html, re.DOTALL)

        if not match:
            # Пробуем другой паттерн
            match = re.search(r'<script[^>]*class="state-view"[^>]*>(.*?)</script>', html, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(1))
                return self._process_route_data(data)
            except json.JSONDecodeError as e:
                print(f"Ошибка парсинга JSON: {e}")

        return None

    def _process_route_data(self, data):
        """
        Обрабатывает JSON данные и находит самый быстрый маршрут

        Args:
            data: JSON данные со страницы

        Returns:
            dict: Информация о самом быстром маршруте
        """
        # Ищем стек с маршрутами
        stacks = data.get('stack', [])

        if not stacks:
            router_response = data.get('routerResponse', {})
            if router_response:
                stacks = [{'routerResponse': router_response}]
            else:
                return None

        for stack in stacks:
            router_response = stack.get('routerResponse', {})
            routes = router_response.get('routes', [])

            if not routes:
                continue

            # Находим самый быстрый маршрут
            fastest = min(routes, key=lambda r: r.get('duration', float('inf')))

            # Извлекаем координаты
            coordinates = self._extract_coordinates(fastest)

            # Формируем результат
            result = {
                'success': True,
                'type': fastest.get('type', 'auto'),
                'duration_seconds': fastest.get('duration', 0),
                'duration_minutes': round(fastest.get('duration', 0) / 60, 1),
                'duration_text': self._format_duration(fastest.get('duration', 0)),
                'distance_meters': fastest.get('distance', {}).get('value', 0),
                'distance_km': round(fastest.get('distance', {}).get('value', 0) / 1000, 1),
                'coordinates': coordinates,
                'waypoints': [],
                'raw_data': fastest
            }

            # Добавляем длительность в пробках если есть
            if 'durationInTraffic' in fastest:
                result['traffic_seconds'] = fastest.get('durationInTraffic', 0)
                result['traffic_minutes'] = round(fastest.get('durationInTraffic', 0) / 60, 1)

            # Извлекаем точки маршрута
            waypoints = router_response.get('waypoints', [])
            for wp in waypoints:
                result['waypoints'].append({
                    'name': wp.get('name', ''),
                    'coordinates': wp.get('coordinates', [])
                })

            return result

        return {'success': False, 'error': 'Маршруты не найдены'}

    def _extract_coordinates(self, route):
        """Извлекает координаты маршрута"""
        paths = route.get('paths', [])

        for path in paths:
            # Проверяем явные координаты
            if 'coordinates' in path and path['coordinates']:
                return path['coordinates']

            # Извлекаем из сегментов
            if 'segments' in path:
                coords = []
                for segment in path['segments']:
                    if 'edgePoints' in segment:
                        coords.extend(segment['edgePoints'])
                if coords:
                    return coords

        return []

    def _format_duration(self, seconds):
        """Форматирует длительность в читаемый вид"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)

        if hours > 0:
            return f"{hours} ч {minutes} мин"
        return f"{minutes} мин"