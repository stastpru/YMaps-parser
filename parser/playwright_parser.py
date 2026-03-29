"""Парсер через Playwright (современная альтернатива Selenium)"""
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from .base import BaseParser


class PlaywrightParser(BaseParser):
    """Парсер маршрутов через Playwright"""

    def __init__(self, headless=True, **kwargs):
        super().__init__(**kwargs)
        self.headless = headless
        self.playwright = None
        self.browser = None
        self.page = None
        self._init_browser()

    def _init_browser(self):
        """Инициализирует браузер через Playwright"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        self.page = self.browser.new_page()
        self.page.set_default_timeout(self.timeout * 1000)  # в миллисекундах

    def get_fastest_route(self, from_point, to_point, mode='auto', region=None, city=None):
        """
        Получает самый быстрый маршрут через Playwright

        Args:
            from_point: Откуда
            to_point: Куда
            mode: Тип маршрута
            region: ID региона
            city: Город

        Returns:
            dict: Данные маршрута
        """
        if not self.page:
            self._init_browser()

        url = self.build_url(from_point, to_point, mode, region, city)
        print(f"Открываю URL: {url}")

        try:
            self.page.goto(url, wait_until='networkidle')

            # Ждем появления маршрутов
            try:
                self.page.wait_for_selector('.route-snippet-view', timeout=self.timeout * 1000)
            except PlaywrightTimeoutError:
                print("Не удалось дождаться загрузки маршрутов")

            html = self.page.content()
            result = self._extract_route_from_html(html)

            if result:
                return result
            else:
                return {'success': False, 'error': 'Не удалось извлечь данные маршрута'}

        except Exception as e:
            return {'success': False, 'error': f'Ошибка: {str(e)}'}

    def close(self):
        """Закрывает браузер"""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()