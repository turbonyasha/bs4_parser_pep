from collections import defaultdict
import logging
from urllib.parse import urljoin
import re

from requests import RequestException
import requests_cache
from tqdm import tqdm

from constants import (
    ALL_VERSIONS, BASE_DIR, DOWNLOADS_DIR, MAIN_DOC_URL, EXPECTED_STATUS,
    LATEST_VERSIONS_HEAD, PEP_HEAD, PEP_URL, TOTAL, WHATS_NEW_HEAD
)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_soup, find_tag

ERROR_MESSAGE = 'Не найден элемент {element}'
SUCCESS_DOWNLOAD = 'Архив был загружен и сохранён: {path}'
PARSER_START = 'Парсер запущен!'
PARSER_FINISH = 'Парсер завершил работу.'
PARSER_ARGS = 'Аргументы командной строки: {args}'
PARSER_ERROR = 'Произошла ошибка в работе парсера: {e}'
URL_NOT_FOUND = 'Не найден url: {e}'


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    results = [WHATS_NEW_HEAD]
    errors = []
    for a_tag in tqdm(
        get_soup(session, whats_new_url).select(
            '#what-s-new-in-python div.toctree-wrapper li.toctree-l1 > a'
        )
    ):
        href = a_tag['href']
        version_link = urljoin(whats_new_url, href)
        try:
            soup = get_soup(session, version_link)
            results.append((
                version_link,
                find_tag(soup, 'h1').text,
                find_tag(soup, 'dl').text.replace('\n', ' ')
            ))
        except RequestException as e:
            errors.append(URL_NOT_FOUND.format(e=e))
    if errors:
        logging.error('\n'.join(errors))
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    ul = next((ul for ul in ul_tags if ALL_VERSIONS in ul.text), None)
    if ul is None:
        raise AttributeError(ERROR_MESSAGE.format(element=ALL_VERSIONS))
    a_tags = ul.find_all('a')
    if not a_tags:
        raise ValueError(ERROR_MESSAGE.format(element='a'))
    results = [LATEST_VERSIONS_HEAD]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    archive_url = urljoin(
        downloads_url,
        soup.select_one(
            'div[role=main] table.docutils a[href$="pdf-a4.zip"]'
        )['href']
    )
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(SUCCESS_DOWNLOAD.format(path=archive_path))


def get_status_from_row(row, session, errors):
    abbr = row.find('abbr')
    link = row.find('a', class_='pep reference internal')
    if abbr and link:
        status = abbr.text.strip()[1:]
        try:
            pep_soup = get_soup(
                session, urljoin(PEP_URL, link.get('href', ''))
            )
            table = pep_soup.find('dl', attrs={
                'class': 'rfc2822 field-list simple'
            })
            if table:
                for dt in table.find_all('dt'):
                    if 'Status' in dt.text:
                        status_tag = dt.find_next_sibling(
                            'dd'
                        ).text.strip()
                        status_from_table = status_tag
                        break
                status = status_from_table if status_from_table else status
                for key, statuses in EXPECTED_STATUS.items():
                    if status in statuses:
                        status = key
                        break
                return status
        except RequestException as e:
            errors.append(URL_NOT_FOUND.format(e=e))
            return None
    return None


def pep(session):
    soup = get_soup(session, PEP_URL)
    rows = soup.find_all('tr', class_=['row-even', 'row-odd'])
    results = defaultdict(int)
    errors = []
    for row in tqdm(rows):
        status = get_status_from_row(row, session, errors)
        if status:
            results[status] += 1
    if errors:
        logging.error('\n'.join(errors))
    return [
        PEP_HEAD,
        *results.items(),
        (TOTAL, sum(results.values())),
    ]


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    try:
        configure_logging()
        logging.info(PARSER_START)
        arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
        args = arg_parser.parse_args()
        logging.info(PARSER_ARGS.format(args=args))
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()
        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
        logging.info(PARSER_FINISH)
    except Exception as e:
        logging.exception(PARSER_ERROR.format(e=e))


if __name__ == '__main__':
    main()
