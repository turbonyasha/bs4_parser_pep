import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import (
    BASE_DIR, LOG_FORMAT, DEFAULT, DT_FORMAT, PRETTY, FILE, LOG_DIR, LOG_FILE
)


def configure_argument_parser(availible_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=availible_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(PRETTY, FILE, DEFAULT),
        default=DEFAULT,
        help='Дополнительные способы вывода данных'
    )
    return parser


def configure_logging():
    log_dir = BASE_DIR / LOG_DIR
    log_dir.mkdir(exist_ok=True)
    rotating_handler = RotatingFileHandler(
        log_dir / LOG_FILE, maxBytes=10 ** 6, backupCount=5, encoding='utf-8'
    )
    logging.basicConfig(
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
