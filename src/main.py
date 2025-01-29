import logging
import re
from urllib.parse import urljoin

import requests_cache
from tqdm import tqdm

from constants import (
    ALL_VERSIONS, BASE_DIR, DOWNLOADS_DIR, MAIN_DOC_URL, EXPECTED_STATUS,
    LATEST_VERSIONS_HEAD, PEP_HEAD, PEP_URL, TOTAL, WHATS_NEW_HEAD
)
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, get_soup, find_tag

ERROR_MESSAGE = 'Не найден элемент {element}'
SUCCESS_DOWNLOAD = 'Архив был загружен и сохранён: {path}'
PARSER_START = 'Парсер запущен!'
PARSER_FINISH = 'Парсер завершил работу.'
PARSER_ARGS = 'Аргументы командной строки: {args}'
PARSER_ERROR = 'Произошла ошибка в работе парсера: {e}'


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    sections_by_python = get_soup(get_response(session, whats_new_url)).select(
        '#what-s-new-in-python div.toctree-wrapper li.toctree-l1'
    )
    results = [WHATS_NEW_HEAD]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = get_soup(get_response(session, version_link))
        results.append((
            version_link,
            find_tag(soup, 'h1').text,
            find_tag(soup, 'dl').text.replace('\n', ' ')
        ))
    return results


def latest_versions(session):
    soup = get_soup(get_response(session, MAIN_DOC_URL))
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    ul = next((ul for ul in ul_tags if ALL_VERSIONS in ul.text), None)
    if ul is None:
        raise ValueError(ERROR_MESSAGE.format(element=ALL_VERSIONS))
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
    soup = get_soup(get_response(session, downloads_url))
    main_div = find_tag(soup, 'div', attrs={'role': 'main'})
    table = find_tag(main_div, 'table', attrs={'class': 'docutils'})
    pdf_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    archive_url = urljoin(downloads_url, pdf_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_DIR
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(SUCCESS_DOWNLOAD.format(path=archive_path))


def pep(session):
    pep_url = PEP_URL
    soup = get_soup(get_response(session, pep_url))
    rows = soup.find_all('tr', class_=['row-even', 'row-odd'])
    count_dict = {}
    for row in tqdm(rows):
        abbr = row.find('abbr')
        link = row.find('a', class_='pep reference internal')
        if abbr and link:
            status = abbr.text.strip()[1:]
            pep_soup = get_soup(get_response(
                session, urljoin(pep_url, link.get('href', ''))
            ))
            table = pep_soup.find('dl', attrs={
                'class': 'rfc2822 field-list simple'
            })
            status_from_table = None
            if table:
                for dt in table.find_all('dt'):
                    if 'Status' in dt.text:
                        status_tag = dt.find_next_sibling('dd').text.strip()
                        status_from_table = status_tag
                        break
                status = status_from_table if status_from_table else status
                for key, statuses in EXPECTED_STATUS.items():
                    if status in statuses:
                        status = key
                        break
                count_dict[status] = count_dict.get(status, 0) + 1
    results = [PEP_HEAD]
    for key, value in count_dict.items():
        if key == '':
            results.append([' ', str(value)])
        else:
            results.append([key, str(value)])
    results.append([TOTAL, str(sum(count_dict.values()))])
    return results


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
