from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_URL = 'https://peps.python.org/'

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'

EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}

BASE_DIR = Path(__file__).parent
LOG_DIR = 'logs'
LOG_FILE = 'parser.log'
RESULTS_DIR = 'results'
DOWNLOADS_DIR = 'downloads'

PRETTY = 'pretty'
FILE = 'file'
ALL_VERSIONS = 'All versions'
WHATS_NEW_HEAD = ('Ссылка на статью', 'Заголовок', 'Редактор, автор')
LATEST_VERSIONS_HEAD = ('Ссылка на документацию', 'Версия', 'Статус')
PEP_HEAD = ['Статус', 'Количество']
TOTAL = 'Всего'
