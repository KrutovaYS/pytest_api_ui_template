"""
Клиент API Aviasales: бизнес-методы поиска билетов.

Использует менеджер cookies для получения валидных cookies и HTTP-клиент
для выполнения запросов с подстановкой заголовков.
Содержит только endpoint'ы и payload'ы.
"""

import time
from typing import Any, Optional

from api.cookie_manager import CookieManager
from api.http_client import AviasalesHttpClient


class AviasalesAPI:
    """
    API-клиент для поиска авиабилетов.

    Управляет search_id и X-Request-Id между запросами; все HTTP-вызовы
    выполняются через AviasalesHttpClient с cookies от CookieManager.
    """

    def __init__(self) -> None:
        """
        Инициализация: создаётся менеджер cookies и HTTP-клиент на его основе.
        """
        cookie_manager = CookieManager()
        self._http_client = AviasalesHttpClient(cookie_manager)
        self.base_url = "https://tickets-api.aviasales.ru"
        self.search_id: Optional[str] = None
        self.last_request_id: Optional[str] = None

    def _make_request(self, method: str, endpoint: str, **kwargs: Any) -> Any:
        """
        Выполняет запрос к API: собирает URL, при необходимости подставляет
        X-Request-Id из предыдущего ответа, вызывает HTTP-клиент и сохраняет
        новый X-Request-Id из заголовков ответа.

        :param method: HTTP-метод (например, 'post').
        :param endpoint: путь относительно base_url
          (например, '/search/v2/start').
        :param kwargs: аргументы для запроса (json, headers и т.д.).
        :return: объект requests.Response.
        """
        url = f"{self.base_url}{endpoint}"

        if self.last_request_id:
            if "headers" not in kwargs:
                kwargs["headers"] = {}
            kwargs["headers"]["X-Request-Id"] = self.last_request_id

        response = self._http_client.request(method, url, **kwargs)

        if "X-Request-Id" in response.headers:
            self.last_request_id = response.headers["X-Request-Id"]

        return response

    def search_start(
        self,
        origin: str,
        destination: str,
        date_from: str,
        date_to: str,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
    ) -> Optional[str]:
        """
        Запускает поиск билетов туда-обратно на указанные даты.

        :param origin: код аэропорта вылета (например, KUF).
        :param destination: код аэропорта прилёта (например, AER).
        :param date_from: дата вылета туда (YYYY-MM-DD).
        :param date_to: дата вылета обратно (YYYY-MM-DD).
        :param adults: количество взрослых.
        :param children: количество детей.
        :param infants: количество младенцев.
        :return: search_id при успехе, None при ошибке ответа.
        """
        payload = {
            "search_params": {
                "directions": [
                    {
                        "origin": origin,
                        "destination": destination,
                        "date": date_from,
                    },
                    {
                        "origin": destination,
                        "destination": origin,
                        "date": date_to,
                    },
                ],
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants": infants,
                },
                "trip_class": "Y",
            },
            "marker": "direct",
            "market_code": "ru",
            "currency_code": "rub",
        }

        response = self._make_request("post", "/search/v2/start", json=payload)

        if response.status_code == 200:
            data = response.json()
            self.search_id = data.get("search_id")
            return self.search_id
        return None

    def search_one_way(
        self,
        origin: str,
        destination: str,
        date: str,
        adults: int = 1,
        children: int = 0,
        infants: int = 0,
    ) -> Optional[str]:
        """
        Запускает поиск билетов в один конец на указанную дату.

        :param origin: код аэропорта вылета.
        :param destination: код аэропорта прилёта.
        :param date: дата вылета (YYYY-MM-DD).
        :param adults: количество взрослых.
        :param children: количество детей.
        :param infants: количество младенцев.
        :return: search_id при успехе, None при ошибке ответа.
        """
        payload = {
            "search_params": {
                "directions": [
                    {
                        "origin": origin,
                        "destination": destination,
                        "date": date,
                    },
                ],
                "passengers": {
                    "adults": adults,
                    "children": children,
                    "infants": infants,
                },
                "trip_class": "Y",
            },
            "marker": "direct",
            "market_code": "ru",
            "currency_code": "rub",
        }

        response = self._make_request("post", "/search/v2/start", json=payload)

        if response.status_code == 200:
            data = response.json()
            self.search_id = data.get("search_id")
            return self.search_id
        return None

    def search_result(self, search_id: Optional[str] = None) -> Optional[list]:
        """
        Запрашивает результаты поиска по search_id
         (несколько попыток при 204/304).

        Перед первым запросом ждёт 2 секунды; при ответах 204/304 повторяет
        до 5 раз с паузой 2 секунды. При 200 и наличии билетов в ответе
        возвращает данные, иначе None.

        :param search_id: идентификатор поиска; если передан, используется он,
            иначе — сохранённый при search_start/search_one_way.
        :return: список данных с билетами при успехе, None при ошибке или
            превышении попыток.
        """
        if search_id is not None:
            self.search_id = search_id

        if not self.search_id:
            return None

        current_timestamp = int(time.time())

        time.sleep(2)

        payload = {
            "limit": 1,
            "price_per_person": False,
            "search_by_airport": False,
            "search_id": self.search_id,
            "last_update_timestamp": current_timestamp,
        }

        for attempt in range(5):
            response = self._make_request(
                "post", "/search/v3.2/results", json=payload
            )

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0 and "tickets" in data[0]:
                    data[0]["tickets"]
                    return data

            elif response.status_code in (204, 304):
                time.sleep(2)
                continue
            else:
                return None

        return None
