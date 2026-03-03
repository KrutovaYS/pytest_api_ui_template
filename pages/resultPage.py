import re
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from pages.mainPage import MainPage


class ResultPage:
    """
    Класс для работы со страницей результатов поиска.
    """
    RESULTS_LIST = (
        By.XPATH,
        '//div[@data-test-id="search-results-items-list"]'
    )

    FIRST_TICKET_PRICE = (By.XPATH, '(//div[@data-test-id="price"])[1]')
    ANY_TICKET_PRICE = (By.XPATH, '//div[@data-test-id="price"]')
    NO_RESULTS_MESSAGE = (
        By.XPATH,
        (
            '//*[contains(., "Ничего не найдено") or contains(., '
            '"Ничего не нашлось")]'
        )
    )
    FAVORITE_BUTTON = (By.XPATH, "(//button[@data-test-id='button'])[1]")
    LOGIN_FORM = (By.XPATH, "//div[@data-test-id='login-form']")
    LOGIN_FORM_TITLE = (
        By.XPATH,
        (
            "//button[@data-test-id='button']"
            "//div[@data-test-id='text' and "
            "contains(normalize-space(.), 'Войти в')]",
        )
    )

    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализирует страницу результатов поиска.

        :param driver: экземпляр Selenium WebDriver.
        """
        self.driver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, 30)

    def wait_for_results_ready(self, timeout: int = 45) -> None:
        """
        Дожидается появления хотя бы одной цены билета на странице.

        :param timeout: максимальное время ожидания в секундах.
        """
        WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(self.ANY_TICKET_PRICE)
        )

    def get_first_price(self) -> str:
        """
        Возвращает цену первого билета в списке результатов.

        :return: строка с ценой.
        """
        price_element = self.wait.until(
            EC.visibility_of_element_located(self.FIRST_TICKET_PRICE)
        )
        return price_element.text.strip()

    def is_price_valid(self, price_text: str) -> bool:
        """
        Проверяет, что строка похожа на цену (содержит хотя бы одну цифру).

        :param price_text: текст цены.
        :return: True, если цена валидна, иначе False.
        """
        if not price_text:
            return False
        return bool(re.search(r"\d", price_text))

    def has_results(self) -> bool:
        """
        Проверяет, что на странице отображается хотя бы одна цена.

        :return: True, если есть результаты, иначе False.
        """
        try:
            short_wait = WebDriverWait(self.driver, 5)
            short_wait.until(
                EC.visibility_of_element_located(self.ANY_TICKET_PRICE)
            )
            return True
        except Exception:
            return False

    def has_no_results(self, timeout: int = 20) -> bool:
        """
        Проверяет сценарий «нет билетов» по сообщению или отсутствию цен.

        :param timeout: максимальное время ожидания в секундах.
        :return: True, если билетов нет, иначе False.
        """
        short_wait = WebDriverWait(self.driver, timeout)

        try:
            msg = short_wait.until(
                EC.visibility_of_element_located(self.NO_RESULTS_MESSAGE)
            )
            if msg and msg.is_displayed():
                return True
        except Exception:
            pass

        try:
            list_el = self.driver.find_element(*self.RESULTS_LIST)
            if list_el.is_displayed():
                prices = self.driver.find_elements(*self.ANY_TICKET_PRICE)
                visible_prices = [p for p in prices if p.is_displayed()]
                if len(visible_prices) == 0:
                    return True
        except Exception:
            pass
        return False

    def click_favourite_button(self) -> None:
        """
        Нажимает на кнопку добавления первого билета в избранное.
        """
        btn_heart = self.wait.until(
            EC.element_to_be_clickable(self.FAVORITE_BUTTON)
        )
        btn_heart.click()

    def is_login_form_displayed(self) -> bool:
        """
        Проверяет, отображается ли форма входа.

        :return: True, если форма входа отображается.
        """
        try:
            return self.wait.until(
                EC.visibility_of_element_located(self.LOGIN_FORM_TITLE)
            ).is_displayed()
        except Exception:
            return False

    def get_login_form_text(self) -> str:
        """
        Возвращает текст заголовка формы входа.

        :return: строка с текстом заголовка формы входа.
        """
        try:
            return self.driver.find_element(*self.LOGIN_FORM_TITLE).text
        except Exception:
            return ""

    def add_to_favourite_without_auth(self) -> str:
        """
        Выполняет поиск и пытается добавить билет в избранное без авторизации.

        :return: текст заголовка формы входа.
        """
        main_page = MainPage(self.driver)
        main_page.open()

        main_page.enter_origin("Владивосток")
        main_page.enter_destination("Самара")
        main_page.enter_date_start("19.03.2026")
        main_page.enter_date_end("20.03.2026")

        main_page.enter_search_btn()
        self.click_favourite_button()

        assert self.is_login_form_displayed(), "Форма входа не появилась"
        return self.get_login_form_text()
