"""Парсер через requests (без браузера)"""
import requests
from .base import BaseParser


class RequestsParser(BaseParser):
    """Парсер маршрутов через прямой HTTP запрос"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def get_fastest_route(self, from_point, to_point, mode='auto', region=None, city=None):
        """
        Получает самый быстрый маршрут через HTTP запрос

        Args:
            from_point: Откуда
            to_point: Куда
            mode: Тип маршрута
            region: ID региона
            city: Город

        Returns:
            dict: Данные маршрута
        """
        url = self.build_url(from_point, to_point, mode, region, city)
        print(f"Запрос к: {url}")

        try:
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()

            result = self._extract_route_from_html(response.text)

            if result:
                return result
            else:
                return {'success': False, 'error': 'Не удалось извлечь данные маршрута'}

        except requests.RequestException as e:
            return {'success': False, 'error': f'Ошибка запроса: {str(e)}'}