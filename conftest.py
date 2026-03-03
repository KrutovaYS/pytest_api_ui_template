import pytest
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options


@pytest.fixture(scope="function")
def driver():
    """
    Фикстура для запуска браузера перед каждым тестом.
    """
    options = Options()
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    driver.implicitly_wait(4)  # Ждем появления элементов до 4 секунд
    yield driver  # Передаем драйвер в тест

    # Проверить перед закрытием
    if driver:
        driver.quit()
