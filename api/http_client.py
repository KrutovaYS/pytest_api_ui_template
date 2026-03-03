"""
HTTP-клиент с подстановкой cookies для запросов к API Aviasales.

Принимает «поставщика cookies» (например, CookieManager), сам формирует
заголовки Cookie, origin, referer и выполняет requests.request(...).
Вся специфика «как вызывать API Aviasales» с точки зрения заголовков
сосредоточена здесь; менеджер cookies остаётся универсальным.
"""

from typing import Any, Protocol
import requests


class CookieProvider(Protocol):
    """
    Протокол для любого объекта, способного отдать валидные cookies.

    Позволяет подставлять разные реализации (файловый кэш, другой сайт,
    мок в тестах) без изменения HTTP-клиента.
    """

    def get_cookies(self) -> dict[str, str]:
        """Возвращает актуальные cookies в виде словаря имя -> значение."""
        ...


class AviasalesHttpClient:
    """
    HTTP-клиент для запросов к Aviasales API с автоматической
    подстановкой cookies.

    Не знает, откуда берутся cookies
    (кэш, Selenium и т.д.) — только запрашивает их
    у поставщика и подставляет в заголовки вместе с
      origin, referer, user-agent.
    """

    # Заголовки, требуемые API Aviasales для принятия запросов.
    DEFAULT_ORIGIN = "https://www.aviasales.ru"
    DEFAULT_REFERER = "https://www.aviasales.ru/"
    DEFAULT_USER_AGENT = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    def __init__(self, cookie_provider: CookieProvider) -> None:
        """
        Инициализация клиента.

        :param cookie_provider: объект
        с методом get_cookies() -> dict[str, str],
            например экземпляр CookieManager.
        """
        self._cookie_provider = cookie_provider

    def request(
        self,
        method: str,
        url: str,
        **kwargs: Any
    ) -> requests.Response:
        """
        Выполняет HTTP-запрос с подстановкой cookies и обязательных заголовков.

        Получает валидные cookies у поставщика,
        формирует строку заголовка Cookie,
        объединяет с переданными в kwargs заголовками
        (переданные имеют приоритет)
        и вызывает requests.request. Также передаёт
        cookies в kwargs для requests,
        чтобы библиотека при необходимости использовала их сама.

        :param method: HTTP-метод (GET, POST и т.д.).
        :param url: полный URL запроса.
        :param kwargs: аргументы для requests.request(headers, json, data и тд)
        :return: ответ requests.Response.
        """
        cookies = self._cookie_provider.get_cookies()
        cookie_header_value = self._format_cookie_header(cookies)

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "user-agent": self.DEFAULT_USER_AGENT,
            "origin": self.DEFAULT_ORIGIN,
            "referer": self.DEFAULT_REFERER,
            "Cookie": cookie_header_value,
        }

        if "headers" in kwargs:
            headers.update(kwargs["headers"])
        kwargs["headers"] = headers
        kwargs["cookies"] = cookies

        return requests.request(method, url, **kwargs)

    def _format_cookie_header(self, cookies: dict[str, str]) -> str:
        """
        Преобразует словарь cookies в строку для HTTP-заголовка Cookie.

        :param cookies: словарь имя_куки -> значение.
        :return: строка вида "name1=value1; name2=value2".
        """
        parts = [f"{name}={value}" for name, value in cookies.items()]
        return "; ".join(parts)
