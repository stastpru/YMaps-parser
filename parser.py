from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
import time
import re


class YandexMapsRouteParser:
    """Парсер маршрутов Яндекс.Карт"""

    def __init__(self, headless=True, download_dir=None):
        """
        Инициализация парсера

        Args:
            headless: Запускать браузер в фоновом режиме
            download_dir: Директория для загрузок
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')

        if download_dir:
            prefs = {'download.default_directory': download_dir}
            chrome_options.add_experimental_option('prefs', prefs)

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 15)

    def build_url(self, from_point, to_point, mode='auto', region='213', city='moscow'):
        """
        Создает URL для маршрута в Яндекс.Картах

        Args:
            from_point: Точка отправления (координаты "lat,lon" или название)
            to_point: Точка назначения (координаты "lat,lon" или название)
            mode: Тип маршрута (auto, masstransit, pedestrian, bicycle, taxi)
            region: ID региона (по умолчанию 213 - Москва)
            city: Город (по умолчанию moscow)

        Returns:
            Сформированный URL
        """
        base_url = f"https://yandex.ru/maps/{region}/{city}/"

        # Если переданы координаты
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
        """
        Создает URL по координатам

        Args:
            from_lat, from_lon: Координаты отправления
            to_lat, to_lon: Координаты назначения
            mode: Тип маршрута

        Returns:
            Сформированный URL
        """
        return self.build_url(f"{from_lat},{from_lon}", f"{to_lat},{to_lon}", mode)

    def parse_route(self, from_point, to_point, mode='auto', region='213', city='moscow'):
        """
        Парсит маршрут по заданным параметрам

        Args:
            from_point: Откуда (координаты "lat,lon" или название)
            to_point: Куда (координаты "lat,lon" или название)
            mode: Тип маршрута
            region: ID региона
            city: Город

        Returns:
            Dict с информацией о самом быстром маршруте
        """
        url = self.build_url(from_point, to_point, mode, region, city)
        print(f"Открываю URL: {url}")

        self.driver.get(url)

        # Ждем загрузки страницы
        time.sleep(5)

        # Ждем появления данных маршрута
        try:
            self.wait.until(
                EC.presence_of_element_located((By.CLASS_NAME, "route-snippet-view"))
            )
        except:
            print("Не удалось дождаться загрузки маршрутов")

        # Получаем HTML и парсим
        html = self.driver.page_source
        return self._extract_route_data(html, mode)

    def _extract_route_data(self, html, mode='auto'):
        """
        Извлекает данные о маршруте из HTML

        Args:
            html: HTML страницы
            mode: Тип маршрута

        Returns:
            Dict с информацией о маршруте
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Ищем скрипт с данными
        state_script = soup.find('script', class_='state-view')

        if not state_script:
            # Пробуем найти данные в других скриптах
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'routerResponse' in script.string:
                    match = re.search(r'{"routes":\[.*?\]}', script.string)
                    if match:
                        try:
                            data = json.loads(match.group())
                            return self._process_route_data(data, mode)
                        except:
                            pass
            return None

        data = json.loads(state_script.string)
        return self._process_route_data(data, mode)

    def _process_route_data(self, data, mode='auto'):
        """
        Обрабатывает JSON данные и находит самый быстрый маршрут
        """
        # Ищем стек с маршрутами
        stacks = data.get('stack', [])

        if not stacks:
            # Пробуем другой путь
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

            # Фильтруем по типу маршрута
            filtered_routes = [r for r in routes if r.get('type') == mode]
            if not filtered_routes:
                filtered_routes = routes

            # Находим самый быстрый маршрут
            fastest = min(filtered_routes, key=lambda r: r.get('duration', float('inf')))

            # Извлекаем координаты
            coordinates = self._extract_coordinates(fastest)

            # Формируем результат
            result = {
                'success': True,
                'type': fastest.get('type', mode),
                'duration_seconds': fastest.get('duration', 0),
                'duration_minutes': round(fastest.get('duration', 0) / 60, 1),
                'duration_text': self._format_duration(fastest.get('duration', 0)),
                'distance_meters': fastest.get('distance', {}).get('value', 0),
                'distance_km': round(fastest.get('distance', {}).get('value', 0) / 1000, 1),
                'coordinates': coordinates,
                'waypoints': [],
                'traffic_duration': None,
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
        """
        Извлекает координаты маршрута
        """
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

            # Из закодированной полилинии
            if 'encodedCoordinates' in path:
                encoded = path['encodedCoordinates']
                if encoded:
                    return self._decode_polyline(encoded)

        return []

    def _decode_polyline(self, encoded):
        """
        Декодирует полилинию (упрощенная версия)
        Для полного декодирования нужна более сложная логика
        """
        # В большинстве случаев координаты уже есть в явном виде
        # Если нет - возвращаем пустой список
        return []

    def _format_duration(self, seconds):
        """Форматирует длительность в читаемый вид"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)

        if hours > 0:
            return f"{hours} ч {minutes} мин"
        return f"{minutes} мин"

    def get_fastest_route(self, from_point, to_point, mode='auto'):
        """
        Основной метод для получения самого быстрого маршрута

        Args:
            from_point: Откуда
            to_point: Куда
            mode: Тип маршрута (auto, masstransit, pedestrian, bicycle, taxi)

        Returns:
            Dict с данными маршрута
        """
        return self.parse_route(from_point, to_point, mode)

    def close(self):
        """Закрывает браузер"""
        self.driver.quit()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


