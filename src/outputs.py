import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (
    BASE_DIR, DATETIME_FORMAT,
    PRETTY, FILE, RESULTS_DIR
)

FILE_MESSAGE = 'Файл с результатами был сохранён: {file_path}'
FILE_NAME = '{parser_mode}_{date}.csv'


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_DIR
    results_dir.mkdir(exist_ok=True)
    file_name = FILE_NAME.format(
        parser_mode=cli_args.mode,
        date=dt.datetime.now().strftime(DATETIME_FORMAT)
    )
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        csv.writer(f, dialect=csv.unix_dialect).writerows(results)
    logging.info(FILE_MESSAGE.format(file_path=file_path))


def default_output(results, cli_args=None):
    for row in results:
        print(*row)


def pretty_output(results, cli_args=None):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


OUTPUT_FUNCTIONS = {
    PRETTY: pretty_output,
    FILE: file_output,
    'console': default_output
}


def control_output(results, cli_args):
    OUTPUT_FUNCTIONS[cli_args.output](results, cli_args)
