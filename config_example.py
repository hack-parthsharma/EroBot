from collections import namedtuple
import os
from pathlib import Path


Rule = namedtuple('Rule', ['alias', 'chat_id', 'log', 'schedule', 'path'])


TOKEN = 'XXX:XXXX'

STORAGE_FILE = 'storage.bin'
LOG_FILE = 'logs/main.log'
PROJECT_PATH = Path(os.path.dirname(os.path.abspath(__file__)))

RULES = (
    Rule(
        alias='ChannelName',
        chat_id=-123,
        log='logs/channelname.log',
        schedule='0 08,13,19,23 * * *',
        path=Path('data'),
    ),
)
