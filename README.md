# pytest_api_ui_template# pytest_UI_API_AviaSales

## Автоматизация тестирования Aviasales

Проект автоматизации тестирования сайта Aviasales.ru
с использованием Selenium WebDriver (UI) и HTTP-запросов (API).

### Стек:
- Pytest
- Selenium
- requests
- allure
- config

### Структура проекта

```
pytest_UI_API_AviaSales/
├── api/                          # Модули для работы с API
│   ├── aviasales_api.py          # Бизнес-методы поиска билетов
│   ├── cookie_manager.py         # Менеджер cookies (кэш + Selenium)
│   └── http_client.py            # HTTP-клиент с заголовками Aviasales
│
├── pages/                        # PageObject для UI-тестов
│   ├── mainPage.py               # Главная страница (форма поиска)
│   └── resultPage.py             # Страница результатов поиска
│
├── test/                         # Тесты
│   ├── test_api.py               # API-тесты
│   └── test_ui.py                # UI-тесты
│
├── conftest.py                    # Фикстуры pytest (WebDriver)
├── pytest.ini                     # Конфигурация pytest
├── requirements.txt                # Зависимости проекта
└── README.md                       # Документация
```

### Полезные ссылки
- Зайти на сайт [Авиасейлс](https://www.aviasales.ru/)
- [Генератор файла .gitignore](https://www.toptal.com/developers/gitignore)
- Финальный проект по ручному тестированию[Авиасейлс](https://skypro-qa110-3.yonote.ru/share/83d73c1c-9d7b-450b-92c2-15a08fc99e46)

### Используемые технологии

- Python 3.13.11
- `pytest` — запуск тестов
- `selenium` — UI‑автоматизация
- `requests` — HTTP‑запросы к API
- `allure-pytest` — отчёты Allure
- `webdriver-manager` — установка ChromeDriver

### UI-тесты (Selenium)

UI-тесты используют PageObject и проверяют функциональность сайта через браузер.

```
Основные сценарии
Тест	                                     Описание
test_search_tickets	                Поиск билетов туда-обратно (Владивосток → Самара, 19.03–20.03)
test_ticket_in_one_way	            Поиск билетов в один конец
test_duble_city	                    Поиск с одинаковыми городами (ожидается сообщение об ошибке)
test_add_to_like	                  Добавление билета в избранное без авторизации (появление формы входа)
test_search_tickets_with_infant	    Поиск с параметром «1 младенец»
```

### Ключевые методы PageObject

#### MainPage (главная страница):

```
python
main_page.open()                            # открыть сайт + принять cookies
main_page.enter_origin("Москва")            # ввести город вылета
main_page.enter_destination("Сочи")         # ввести город назначения
main_page.enter_date_start("19.03.2026")    # выбрать дату вылета
main_page.enter_date_end("20.03.2026")      # выбрать дату возвращения
main_page.enter_search_btn()                # нажать «Найти билеты»
main_page.add_infant()                      # добавить младенца
```

#### ResultPage (результаты поиска):

```
python
result_page.wait_for_results_ready()        # дождаться загрузки результатов
result_page.get_first_price()               # получить цену первого билета
result_page.is_price_valid()                # проверить формат цены
result_page.has_no_results()                # проверить отсутствие билетов
result_page.click_favourite_button()        # нажать «Избранное»
```

### API-тесты (HTTP)

API-тесты взаимодействуют с внутренним API Aviasales через эндпоинты поиска.

Механизм работы
CookieManager получает cookies через headless Chrome (кэш на 30 мин)

AviasalesHttpClient формирует заголовки и выполняет запросы

AviasalesAPI реализует бизнес-методы поиска

#### Основные сценарии

```
Тест	                               Описание
test_search_specific_dates	      Поиск туда-обратно на конкретные даты
test_search_one_way	              Поиск в один конец
test_search_several_months      	Поиск с диапазоном в несколько месяцев
test_search_with_infant         	Поиск с младенцем
test_duplicate_city	              Негативный тест (одинаковые города)
```

### Установка и запуск

1. Клонирование репозитория
bash
git clone https://github.com/KrutovaYS/pytest_api_ui_template.git
cd pytest_api_ui_template

2. Установка зависимостей

```bash
pip install -r requirements.txt
```

3. Запуск тестов
bash
#### Все тесты
pytest

#### Только UI-тесты
pytest -m ui

#### Только API-тесты
pytest -m api

#### С подробным выводом
pytest -v -s



### Allure‑отчёты

Все тесты размечены аннотациями Allure:

- `@allure.title` — человекочитаемый заголовок теста;
- `@allure.story` — сценарий/подраздел фичи;
- `@allure.description` — детальное описание;
- `@allure.feature` - фича
- `@allure.severity` - критичность
- `with allure.step("…")` — шаги внутри тестов.

Генерация отчёта Allure:

```bash
pytest --alluredir=allure-results
allure serve allure-results
```

или для статического отчёта:

```bash
allure generate allure-results -o allure-report --clean
```

### Примечания

- В UI‑тестах используются фиксированные города и даты; при изменении поведения сайта локаторы и данные могут потребовать обновления.
- Для API‑тестов важно, чтобы эндпоинты и формат запросов Aviasales не изменились.
- UI- тесты выполняются медленно