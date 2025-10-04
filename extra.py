# Constants
from datetime import datetime
INPUT = "\033[32m{}\033[34m{}\033[0m"   # GREEN
ERROR = "\033[31m{}\033[0m"             # RED
DEBUG = "\033[33;1m{}\033[0m"           # YELLOW
EXTRA = "\033[34m{}\033[0m"             # BLUE

MONTHS = ['Январь', 'Февраль', 'Март',
          'Апрель', 'Май', 'Июнь',
          'Июль', 'Август', 'Сентябрь',
          'Октябрь', 'Ноябрь', 'Декабрь']

EMULATOR_START_TIME = datetime.now().strftime("%Y-%m-%d %H:%M")