import re
from urllib.parse import urljoin
import logging

from bs4 import BeautifulSoup
import requests_cache
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def whats_new(session):
    # Вместо константы WHATS_NEW_URL, используйте переменную whats_new_url.
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper compound'})
    sections_by_python = div_with_ul.find_all('li', attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    # Вместо константы DOWNLOADS_URL, используйте переменную downloads_url.
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'div', attrs={'role': 'main'})
    table = find_tag(main_div, 'table', attrs={'class': 'docutils'})
    pdf_tag = find_tag(table, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    archive_url = urljoin(downloads_url, pdf_tag['href'])
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    pep_url = 'https://peps.python.org/'
    response = get_response(session, pep_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    rows = soup.find_all('tr', class_='row-even')
    pep_count = 0
    count_dict = {}
    for row in rows:
        abbr = row.find('abbr')
        link = row.find('a', class_='pep reference internal')
        if abbr and link:
            status = abbr.text.strip()
            link_href = link.get('href', '')
            pep_count += 1
            pep_link = urljoin(pep_url, link_href)
            response = get_response(session, pep_link)
            if response is None:
                return
            soup = BeautifulSoup(response.text, features='lxml')
            table = soup.find('dl', attrs={'class': 'rfc2822 field-list simple'})
            for dt in table.find_all('dt'):
                if 'Status' in dt.text:
                    status_tag = dt.find_next_sibling('dd').text
                    if status_tag != status:
                        status = status_tag
                    if status_tag in count_dict:
                        count_dict[status_tag] += 1
                    else:
                        count_dict[status_tag] = 1
                    break
    print('Нахождение строк', pep_count)
    print(count_dict)
    print('Сумма в словаре', sum(count_dict.values()))


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
