import logging
from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url):
    try:
        response = session.get(url)
        response.encoding = 'utf-8'
        return response
    except RequestException:
        logging.exception(
            f'Возникла ошибка при загрузке страницы {url}',
            stack_info=True
        )


def find_tag(soup, tag, attrs=None, string=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}), string=string)
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        logging.error(error_msg, stack_info=True)
        raise ParserFindTagException(error_msg)
    return searched_tag


def write_pep_file(results_path, count_dict):
    with open(results_path, 'w', encoding='utf-8') as file:
        file.write('Статус Количество\n')
        for key, value in count_dict.items():
            if key == '':
                file.write(f'" ": {value}\n')
            else:
                file.write(f'{key}: {value}\n')
        file.write(f'Total {sum(count_dict.values())}')
