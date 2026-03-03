from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys


base_url = "https://www.aviasales.ru/"


class MainPage:
    COOKIE_ACCEPT_BUTTON = (
        By.XPATH,
        "//button[@data-test-id='accept-cookies-button']"
    )

    ORIGIN_INPUT = (By.XPATH, "//input[@data-test-id='origin-input']")

    DESTINATION_INPUT = (
        By.XPATH,
        "//input[@data-test-id='destination-input']"
        )

    DATE_START = (By.XPATH, "//button[@data-test-id='start-date-field']")
    DATE_END = (By.CSS_SELECTOR, "[data-test-id='end-date-value']")
    SEARCH_BUTTON = (By.XPATH, "//button[@data-test-id='form-submit']")
    PASSENGERS_FIELD = (By.XPATH, "//button[@data-test-id='passengers-field']")
    INFANTS_PLUS_BUTTON = (
        By.XPATH,
        "(//button[@data-test-id='increase-button'])[3]"
    )

    INFANTS_COUNS = (
        By.XPATH,
        (
            "//div[@data-test-id='number-of-infants']"
            "//div[@data-test-id='passenger-number']"
        )
    )

    DATE_CALENDAR = (By.XPATH, "//div[@data-test-id='dropdown']")
    DATE_DAY_IN_CALENDAR = (By.XPATH, "//div[@data-test-id='date-19.03.2026']")
    ORIGIN_SUGGEST = (By.XPATH, "//ul[@id='avia_form_origin-menu']")
    DESTINATION_SUGGEST = (By.CSS_SELECTOR, "ul.suggest__list li:first-child")
    PASSENGERS_INFO = (
        By.XPATH,
        "(//div[@data-test-id='trip-class-and-number-passengers'])[3]"
    )

    def __init__(self, driver: WebDriver) -> None:
        """
        Инициализирует главную страницу, настраивая драйвер и явные ожидания.

        :param driver: экземпляр Selenium WebDriver.
        """
        self.driver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, 10)

    def open(self) -> None:
        """
        Открывает главную страницу и принимает cookies,
          если баннер отображается.
        """
        self.driver.execute_cdp_cmd(
            'Page.setLifecycleEventsEnabled',
            {'enabled': False}
        )
        self.driver.get(base_url)
        self.wait.until(
            EC.presence_of_element_located(self.COOKIE_ACCEPT_BUTTON)
        )
        self.accept_cookies()

    def accept_cookies(self) -> bool:
        """
        Принимает cookies при наличии баннера.

        :return: True, если баннера нет или он успешно скрыт.
        """
        cookie_btn = self.wait.until(
            EC.element_to_be_clickable(self.COOKIE_ACCEPT_BUTTON)
        )
        cookie_btn.click()
        assert self.wait.until(
            EC.invisibility_of_element_located(self.COOKIE_ACCEPT_BUTTON)
        ), "Не пропал баннер куки"
        return True

    def enter_origin(self, city: str) -> None:
        """
        Вводит город вылета в поле «Откуда» и выбирает вариант из подсказок.

        :param city: название города вылета.
        """
        origin_field = self.wait.until(
            EC.element_to_be_clickable(self.ORIGIN_INPUT)
        )
        try:
            self.wait.until(
                lambda driver: origin_field.get_attribute('value') != ''
            )
        except Exception:
            pass

        origin_field.clear()
        origin_field.send_keys(Keys.CONTROL + 'a')
        origin_field.send_keys(Keys.DELETE)
        origin_field.send_keys(city)

        self.wait.until(EC.element_to_be_clickable(self.ORIGIN_SUGGEST))

        try:
            vvo_locator = (By.XPATH, "//li[contains(text(), 'VVO')]")
            vvo_option = self.wait.until(
                EC.element_to_be_clickable(vvo_locator)
            )
            vvo_option.click()
        except Exception:
            try:
                first_option = self.driver.find_element(*self.ORIGIN_SUGGEST)
                first_option.click()
            except Exception:
                origin_field.send_keys(Keys.RETURN)

        origin_field = self.wait.until(
            EC.presence_of_element_located(self.ORIGIN_INPUT)
        )
        assert origin_field.get_attribute('value') == city

    def enter_destination(self, city_destination: str) -> None:
        """
        Вводит город назначения в поле "Куда".

        :param city_destination: название города назначения.
        """
        dest_city = self.wait.until(
            EC.element_to_be_clickable(self.DESTINATION_INPUT)
        )
        dest_city.clear()
        dest_city.send_keys(city_destination)

        try:
            suggest = self.wait.until(
                EC.element_to_be_clickable(self.DESTINATION_SUGGEST)
            )
            suggest.click()
        except Exception:
            dest_city.send_keys(Keys.RETURN)

    def enter_date_start(self, start_date: str) -> str:
        """
        Выбирает дату вылета в календаре.

        :param start_date: дата вылета в формате DD.MM.YYYY.
        :return: текстовое значение выбранной даты в поле.
        """
        date_start = self.wait.until(
            EC.element_to_be_clickable(self.DATE_START)
        )
        date_start.click()
        self.wait.until(EC.visibility_of_element_located(self.DATE_CALENDAR))

        button_locator = (
            By.XPATH,
            f"//div[@data-test-id='date-{start_date}']/ancestor::button",
        )
        day_button = self.wait.until(
            EC.element_to_be_clickable(button_locator)
        )
        day_button.click()

        date_field = self.wait.until(
            EC.presence_of_element_located(self.DATE_START)
        )
        return date_field.text

    def enter_date_end(self, end_date) -> str:
        """
        Выбирает дату возвращения/прибытия в календаре.

        :param end_date: дата возвращения в формате DD.MM.YYYY.
        :return: текстовое значение выбранной даты в поле.
        """
        date_end = self.wait.until(
            EC.element_to_be_clickable(self.DATE_END)
        )
        date_end.click()
        self.wait.until(EC.visibility_of_element_located(self.DATE_CALENDAR))

        DATE_BUTTON_LOCATOR = (
            By.XPATH,
            f"//div[@data-test-id='date-{end_date}']/ancestor::button",
        )
        day_button = self.wait.until(
            EC.element_to_be_clickable(DATE_BUTTON_LOCATOR)
        )
        day_button.click()

        date_field = self.wait.until(
            EC.presence_of_element_located(self.DATE_END)
        )
        return date_field.text

    def enter_search_btn(self):
        """
        Нажимает кнопку поиска билетов и ждёт перехода на страницу результатов.
        """
        search_btn = self.wait.until(
            EC.element_to_be_clickable(self.SEARCH_BUTTON)
        )
        search_btn.click()

        WebDriverWait(self.driver, 20).until(
            lambda d: any(
                s in d.current_url for s in ("search", "params=", "aviasales")
            ),
            message="URL не обновился до страницы поиска/результатов за 20 с",
        )

        current_url = self.driver.current_url
        assert (
            "search" in current_url
            or "aviasales" in current_url
            or "params=" in current_url
        ), "Ожидалась страница поиска или главная"

        self.switch_to_results_tab()

    def switch_to_results_tab(self):
        """
        Переключается на вкладку с результатами поиска, если она открыта.
        """
        if len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])

    def add_infant(self) -> str:
        """ Добавляет младенца в параметры поиска.

        :return: текстовое значение количества младенцев после изменения.
        """
        passengers_field = self.wait.until(
            EC.element_to_be_clickable(self.PASSENGERS_FIELD)
        )
        passengers_field.click()

        infant_plus = self.wait.until(
            EC.element_to_be_clickable(self.INFANTS_PLUS_BUTTON)
        )
        infant_plus.click()

        passenger_info = self.wait.until(
            EC.visibility_of_element_located(self.INFANTS_COUNS)
        )
        passenger_text = passenger_info.text

        self.driver.find_element(By.TAG_NAME, "body").click()

        return passenger_text
