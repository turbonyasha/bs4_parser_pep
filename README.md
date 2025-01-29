# Парсер версий и документации для Python и статусов для PEP

Проект представляет собой Python-программу для парсинга информации с сайтов [Python](https://docs.python.org/3/) и [PEP](https://peps.python.org/).

Программа использует библиотеки `BeautifulSoup` и `requests` для парсинга HTML и HTTP-запросов, а также поддерживает кэширование с использованием `requests_cache` для ускорения запросов. Результаты могут быть выведены в различных форматах: таблица формата PrettyTable или CSV-файл.

## Возможности

- Парсинг актуальных данных о статусах всех существующих PEP;
- Скачивание архива документации для последней версии Python;
- Сбор ссылок на документацию и ее авторов для каждой версии Python;
- Поддержка вывода результатов в форматах:
  - Таблица (с использованием библиотеки `PrettyTable`);
  - CSV файл;
- Кэширование запросов для ускорения работы;
- Очистка кэша по запросу;
- Логгирование всех этапов выполнения и ошибок.

## Установка

1. Клонируйте репозиторий:
    ```
    git clone git@github.com:turbonyasha/bs4_parser_pep.git
    ```

2. Перейдите в каталог проекта:
    ```
    cd bs4_parser_pep
    ```

3. Создайте и активируйте виртуальное окружение:
    ```
    python -m venv venv
    source venv/bin/activate  # Для Linux/macOS
    venv\Scripts\activate  # Для Windows
    ```

4. Установите зависимости:
    ```
    pip install -r requirements.txt
    ```

## Использование

Для запуска парсера перейдите в каталог scr проекта:
```
cd src
```

Используйте желаемую команду следующего вида:

```
usage: main.py [-h] [-c] [-o {pretty,file}] {whats-new,latest-versions,download,pep}

Парсер документации Python

positional arguments:
  {whats-new,latest-versions,download,pep}
                        Режимы работы парсера

optional arguments:
  -h, --help            show this help message and exit
  -c, --clear-cache     Очистка кеша
  -o {pretty,file}, --output {pretty,file}
                        Дополнительные способы вывода данных
```
