import allure
import pytest
from api.aviasales_api import AviasalesAPI

pytestmark = pytest.mark.api


@allure.feature(
        "Сайт Авиасейлс - сервис по поиску "
        "и бронированию авиабилетов"
)
@allure.title("API: Поиск билетов туда-обратно без авторизации")
@allure.story("API поиска билетов")
@allure.description(
    "Проверка успешного старта поиска билетов "
    "на конкретные даты и получения результатов."
)
@allure.severity(allure.severity_level.CRITICAL)
def test_search_specific_dates() -> None:
    api = AviasalesAPI()

    with allure.step("Отправить запрос на старт поиска туда-обратно"):
        search_id = api.search_start(
            origin='KUF',
            destination='AER',
            date_from='2026-11-08',
            date_to='2026-11-09',
            adults=1
        )
        assert search_id is not None

    with allure.step("Запросить результаты поиска по search_id"):
        results = api.search_result(search_id)
        assert results is not None


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("API: Поиск билетов в один конец")
@allure.story("API поиска билетов")
@allure.description(
    "Проверка успешного поиска билета "
    "в один конец и получения результатов."
)
@allure.severity(allure.severity_level.CRITICAL)
def test_search_one_way() -> None:
    api = AviasalesAPI()

    with allure.step("Отправить запрос на старт поиска в один конец"):
        search_id = api.search_one_way(
            origin='KUF',
            destination='AER',
            date='2026-11-08',
            adults=1
        )
        assert search_id is not None

    with allure.step("Запросить результаты поиска по search_id"):
        results = api.search_result(search_id)
        assert results is not None


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("API: Поиск с диапазоном дат в несколько месяцев")
@allure.story("API поиска билетов")
@allure.description(
    "Проверка поиска билетов с большим "
    "диапазоном дат (несколько месяцев)."
)
@allure.severity(allure.severity_level.CRITICAL)
def test_search_several_months() -> None:
    api = AviasalesAPI()

    with allure.step(
        "Отправить запрос на старт поиска "
        "с большим диапазоном дат"
    ):
        search_id = api.search_start(
            origin='KUF',
            destination='AER',
            date_from='2026-11-08',
            date_to='2027-02-08',
            adults=1
        )
        assert search_id is not None

    with allure.step("Запросить результаты поиска по search_id"):
        results = api.search_result(search_id)
        assert results is not None


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("API: Поиск с 1 взрослым и 1 младенцем")
@allure.story("API поиска билетов")
@allure.description("Проверка поиска билетов для 1 взрослого и 1 младенца.")
@allure.severity(allure.severity_level.CRITICAL)
def test_search_with_infant() -> None:
    api = AviasalesAPI()

    with allure.step("Отправить запрос на старт поиска с младенцем"):
        search_id = api.search_start(
            origin='KUF',
            destination='AER',
            date_from='2026-11-08',
            date_to='2026-11-09',
            adults=1,
            infants=1
        )

    with allure.step("Запросить результаты поиска по search_id"):
        results = api.search_result(search_id)
        assert results is not None


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("API: Негативный сценарий с дублированием города")
@allure.story("API поиска билетов")
@allure.description(
    "Проверка обработки запроса, "
    "когда город вылета и прилёта совпадают."
)
@allure.severity(allure.severity_level.CRITICAL)
def test_duplicate_city() -> None:
    api = AviasalesAPI()

    with allure.step(
        "Отправить запрос на старт поиска "
        "с одинаковыми городами"
    ):
        search_id = api.search_start(
            origin='KUF',
            destination='KUF',
            date_from='2026-11-08',
            date_to='2026-11-09',
            adults=1
        )
        assert search_id is None
