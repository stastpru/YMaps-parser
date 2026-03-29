"""Парсер через Selenium (с открытием браузера)"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from .base import BaseParser


class SeleniumParser(BaseParser):
    """Парсер маршрутов через Selenium с Chrome"""

    def __init__(self, headless=True, **kwargs):
        super().__init__(**kwargs)
        self.headless = headless
        self.driver = None
        self._init_driver()

    def _init_driver(self):
        """Инициализирует Chrome драйвер"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless')

        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])

        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, self.timeout)
        except WebDriverException as e:
            raise Exception(f"Не удалось инициализировать ChromeDriver: {e}")

    def get_fastest_route(self, from_point, to_point, mode='auto', region=None, city=None):
        """
        Получает самый быстрый маршрут через Selenium

        Args:
            from_point: Откуда
            to_point: Куда
            mode: Тип маршрута
            region: ID региона
            city: Город

        Returns:
            dict: Данные маршрута
        """
        if not self.driver:
            self._init_driver()

        url = self.build_url(from_point, to_point, mode, region, city)
        print(f"Открываю URL: {url}")

        try:
            self.driver.get(url)

            # Ждем загрузки страницы
            time.sleep(3)

            # Ждем появления маршрутов
            try:
                self.wait.until(
                    EC.presence_of_element_located((By.CLASS_NAME, "route-snippet-view"))
                )
            except TimeoutException:
                print("Не удалось дождаться загрузки маршрутов")

            # Даем время для полной загрузки динамического контента
            time.sleep(2)

            html = self.driver.page_source
            result = self._extract_route_from_html(html)

            if result:
                return result
            else:
                return {'success': False, 'error': 'Не удалось извлечь данные маршрута'}

        except Exception as e:
            return {'success': False, 'error': f'Ошибка: {str(e)}'}

    def close(self):
        """Закрывает браузер"""
        if self.driver:
            self.driver.quit()
            self.driver = None