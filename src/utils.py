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
    except ConnectionError as e:
        raise ConnectionError(
            LOG_MESSAGE.format(url=url, e=e)
        )


def get_soup(session, url, features='lxml'):
    return BeautifulSoup(get_response(session, url).text, features=features)


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
