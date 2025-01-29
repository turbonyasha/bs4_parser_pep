import logging
from requests import RequestException

from bs4 import BeautifulSoup

from exceptions import ParserFindTagException

LOG_MESSAGE = 'Возникла ошибка при загрузке страницы {url}: {e}'
NOT_FOUND_MESSAGE = 'Не найден тег {tag} {attrs}'
EMPTY_ANSWER = 'Пустой ответ для {url}'


def get_response(session, url, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException as e:
        raise Exception(
            LOG_MESSAGE.format(url=url, e=e)
        )


def get_soup(response):
    try:
        if response is None:
            logging.error(EMPTY_ANSWER.format(url=response.url))
            return
        return BeautifulSoup(response.text, features='lxml')
    except RequestException as e:
        raise Exception(
            LOG_MESSAGE.format(url=response.url, e=e)
        )


def find_tag(soup, tag, attrs=None, string=''):
    searched_tag = soup.find(
        tag, attrs=({} if attrs is None else attrs), string=string
    )
    if searched_tag is None:
        raise ParserFindTagException(
            NOT_FOUND_MESSAGE.format(
                tag=tag, attrs=attrs
            ))
    return searched_tag
