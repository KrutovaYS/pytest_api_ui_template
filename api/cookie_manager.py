"""
Менеджер cookies: единственная ответственность — предоставить валидные cookies.

Не знает про HTTP, заголовки, origin/referer. Логика «когда брать из кэша,
когда обновлять через Selenium» сосредоточена здесь; хранилище и TTL можно
подменять без изменения вызывающего кода.
"""
import requests
import json
import os
from datetime import datetime, timedelta
from typing import Optional

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


class CookieManager:
    """
    Поставщик валидных cookies для Aviasales.

    Кэширует cookies в файл с TTL; при истечении или отсутствии кэша
    получает свежие cookies через headless Selenium.
    """

    def __init__(self, cookie_file: str = "aviasales_cookies.json") -> None:
        """
        Инициализация менеджера.

        :param cookie_file: путь к файлу для кэширования cookies (по умолчанию
            aviasales_cookies.json в текущей директории).
        """
        self.cookie_file = cookie_file

    def get_cookies(self) -> dict[str, str]:
        """
        Единственная публичная точка входа: всегда возвращает валидные cookies.

        Сначала пытается загрузить из хранилища (файл + проверка TTL).
        Если кэш отсутствует или просрочен — получает свежие cookies через
        Selenium, сохраняет в хранилище и возвращает их.

        :return: словарь имя_куки -> значение (готов для подстановки в
         заголовки или в requests).
        """
        cookies = self._load_cookies()
        if cookies is not None:
            return cookies
        cookies = self._get_fresh_cookies()
        self._save_cookies(cookies)
        return cookies

    def _load_cookies(self) -> Optional[dict[str, str]]:
        """
        Загружает cookies из файлового кэша, если файл есть и TTL не истёк.

        :return: словарь cookies или None, если кэш недоступен или просрочен.
        """
        if not os.path.exists(self.cookie_file):
            return None
        with open(self.cookie_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        expires = datetime.fromisoformat(data["expires"])
        if datetime.now() < expires:
            return data["cookies"]
        return None

    def _save_cookies(self, cookies: dict[str, str]) -> None:
        """
        Сохраняет cookies в файл с указанием времени истечения (TTL 30 минут).

        :param cookies: словарь имя_куки -> значение.
        """
        data = {
            "cookies": cookies,
            "expires": (datetime.now() + timedelta(minutes=30)).isoformat(),
        }
        with open(self.cookie_file, "w", encoding="utf-8") as f:
            json.dump(data, f)

    def _get_fresh_cookies(self) -> dict[str, str]:
        """
        Получает свежие cookies с сайта Aviasales через headless Chrome.

        Открывает страницу, ждёт загрузки body, собирает cookies из драйвера
        и возвращает их в виде словаря. Драйвер всегда закрывается в finally.

        :return: словарь имя_куки -> значение.
        """
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=options
        )

        try:
            driver.get("https://www.aviasales.ru")
            wait = WebDriverWait(driver, 10)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            cookies: dict[str, str] = {}
            for cookie in driver.get_cookies():
                cookies[cookie["name"]] = cookie["value"]
            return cookies
        finally:
            driver.quit()

    def save_cookies(self, cookies):
        data = {
            'cookies': cookies,
            'expires': (datetime.now() + timedelta(minutes=30)).isoformat()
        }
        with open(self.cookie_file, 'w') as f:
            json.dump(data, f)

    def load_cookies(self):
        if not os.path.exists(self.cookie_file):
            return None
        with open(self.cookie_file, 'r') as f:
            data = json.load(f)
        expires = datetime.fromisoformat(data['expires'])
        if datetime.now() < expires:
            return data['cookies']
        return None

    def get_valid_cookies(self):
        cookies = self.load_cookies()
        if cookies:
            return cookies
        cookies = self.get_fresh_cookies()
        self.save_cookies(cookies)
        return cookies

    def format_cookie_header(self, cookies):
        cookie_parts = []
        for name, value in cookies.items():
            cookie_parts.append(f"{name}={value}")
        return '; '.join(cookie_parts)

    def request(self, method, url, **kwargs):
        cookies = self.get_valid_cookies()

        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'user-agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36'
            ),
            'origin': 'https://www.aviasales.ru',
            'referer': 'https://www.aviasales.ru/',
            'Cookie': self.format_cookie_header(cookies)
        }

        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        kwargs['cookies'] = cookies

        return requests.request(method, url, **kwargs)
