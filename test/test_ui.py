import allure
import pytest
from selenium.webdriver.remote.webdriver import WebDriver
from pages.resultPage import ResultPage
from pages.mainPage import MainPage

pytestmark = pytest.mark.ui


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("UI: Поиск билетов туда-обратно без авторизации")
@allure.story("Поиск билетов")
@allure.description(
    "Проверка базового сценария поиска билетов "
    "на конкретные даты без авторизации."
)
@allure.severity("Critical")
def test_search_tickets(driver: WebDriver) -> None:
    main_page = MainPage(driver)
    result_page = ResultPage(driver)

    with allure.step("Открыть главную страницу АВиасейлс"):
        main_page.open()

    with allure.step("Заполнить форму поиска: города и даты вылета/возврата"):
        main_page.enter_origin('Владивосток')
        main_page.enter_destination('Самара')
        main_page.enter_date_start('19.03.2026')
        main_page.enter_date_end('20.03.2026')

    with allure.step("Нажать кнопку 'Найти билеты'"):
        main_page.enter_search_btn()

    with allure.step("Дождаться результатов и проверить цену первого билета"):
        result_page.wait_for_results_ready(timeout=45)
        first_price = result_page.get_first_price()
        assert first_price, "Цена первого билета не найдена"
        assert result_page.is_price_valid(first_price), (
            f"Цена не похожа на число: '{first_price}'"
        )


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("UI: Поиск билетов в один конец")
@allure.story("Поиск билетов")
@allure.description("Проверка сценария поиска билетов в один конец.")
@allure.severity("Critical")
def test_ticket_in_one_way(driver: WebDriver) -> None:
    main_page = MainPage(driver)
    result_page = ResultPage(driver)

    with allure.step("Открыть главную страницу АВиасейлс"):
        main_page.open()

    with allure.step("Заполнить форму поиска: города и дату вылета"):
        main_page.enter_origin('Владивосток')
        main_page.enter_destination('Сочи')
        main_page.enter_date_start('19.03.2026')

    with allure.step("Нажать кнопку 'Найти билеты'"):
        main_page.enter_search_btn()

    with allure.step("Дождаться результатов и проверить цену первого билета"):
        result_page.wait_for_results_ready(timeout=40)
        first_price = result_page.get_first_price()
        assert first_price, "Цена первого билета не найдена"
        assert result_page.is_price_valid(first_price), (
            f"Цена не похожа на число: '{first_price}'"
        )
        print(f"Цена первого билета: {first_price}")


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("UI: Поиск с дублированием городов Откуда и Куда")
@allure.story("Негативные сценарии поиска")
@allure.description(
    "Проверка поведения системы при дублировании "
    "города отправления и назначения."
)
@allure.severity("Critical")
def test_duble_city(driver: WebDriver) -> None:
    main_page = MainPage(driver)
    result_page = ResultPage(driver)

    with allure.step("Открыть главную страницу АВиасейлс"):
        main_page.open()

    with allure.step("Заполнить форму поиска одинаковыми городами и датами"):
        main_page.enter_origin('Владивосток')
        main_page.enter_destination('Владивосток')
        main_page.enter_date_start('19.03.2026')
        main_page.enter_date_end('20.03.2026')

    with allure.step("Нажать кнопку 'Найти билеты'"):
        main_page.enter_search_btn()

    with allure.step("Проверить, что билеты не найдены"):
        assert result_page.has_no_results(), (
            "Ожидалось сообщение об отсутствии билетов "
            "или пустой список результатов"
        )


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("UI: Добавление билета в избранное без авторизации")
@allure.story("Избранное")
@allure.description(
    "Проверка появления формы входа при попытке "
    "добавить билет в избранное без авторизации."
)
@allure.severity("Critical")
def test_add_to_like(driver: WebDriver) -> None:
    result_page = ResultPage(driver)

    with allure.step(
        "Открыть результаты поиска и попытаться "
        "добавить билет в избранное"
    ):
        login_form_text = result_page.add_to_favourite_without_auth()

    with allure.step("Проверить текст формы входа"):
        assert login_form_text == "Войти в профиль"


@allure.feature("Сайт Авиасейлс - сервис по поиску и бронированию авиабилетов")
@allure.title("UI: Поиск билетов с младенцем")
@allure.story("Поиск билетов")
@allure.description("Проверка поиска билетов для 1 взрослого и 1 младенца.")
@allure.severity("Critical")
def test_search_tickets_with_infant(driver: WebDriver) -> None:
    main_page = MainPage(driver)
    result_page = ResultPage(driver)

    with allure.step("Открыть главную страницу АВиасейлс"):
        main_page.open()

    with allure.step("Заполнить форму поиска: города и даты вылета/возврата"):
        main_page.enter_origin('Владивосток')
        main_page.enter_destination('Сочи')
        main_page.enter_date_start('19.03.2026')
        main_page.enter_date_end('20.03.2026')

    with allure.step("Добавить в поиск 1 младенца и проверяем"):
        infant_text = main_page.add_infant()
        assert infant_text == "1", f"Ожидалось 1, получено: {infant_text}"

    with allure.step("Выполнить поиск и дождаться результатов"):
        main_page.enter_search_btn()
        result_page.wait_for_results_ready(timeout=60)
