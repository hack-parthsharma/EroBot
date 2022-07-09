# built-in
import os
import os.path
import pickle
import random
import time
from collections import namedtuple
from contextlib import contextmanager

# project
import config
from crontab import CronTab
from settings import bot

State = namedtuple('State', ['queue', 'sended', 'failed'])


class Channel:
    def __init__(self, rule, state=None):
        self.rule = rule
        self.state = state

    def get_all_files(self):
        # make dir if not exists
        if not self.rule.path.is_dir():
            self.rule.path.mkdir()
        # read files from dir
        return list(self.rule.path.iterdir())

    def flush(self):
        # read
        files = self.get_all_files()
        # shuffle
        random.shuffle(files)
        # flush state
        self.state = State(
            queue=files,
            sended=[],
            failed=[],
        )
        # return new state
        return self.state

    def update(self):
        files = self.get_all_files()
        # find diff (deleted and added files)
        diff_files = list((set(files) ^ set(self.state.queue)) - set(self.state.sended))
        # get new queue
        queue = list(set(files) - set(self.state.sended))
        # shuffle queue
        random.shuffle(queue)
        # update queue in state
        self.state = self.state._replace(queue=queue)
        return diff_files

    def create_cron_task(self):
        cron = CronTab()
        job = cron.new(command='python3 {} "{}"'.format(
            config.PROJECT_PATH / 'send.py',
            self.rule.alias,
        ))
        job.setall('0 08,13,19,23 * * *')
        return cron.write()

    def _send_file(self, file_descriptor, ext, caption):
        if ext in ('.jpg', '.png'):
            return bot.send_photo(
                chat_id=self.rule.chat_id,
                photo=file_descriptor,
                caption=caption,
            )
        elif ext == '.txt':
            return bot.send_message(
                chat_id=self.rule.chat_id,
                text=file_descriptor.read().decode(),
            )
        elif ext == '.md':
            return bot.send_message(
                chat_id=self.rule.chat_id,
                text=file_descriptor.read().decode(),
                parse_mode='Markdown',
            )
        elif ext == '.html':
            return bot.send_message(
                chat_id=self.rule.chat_id,
                text=file_descriptor.read().decode(),
                parse_mode='HTML',
            )
        elif ext == '.mp3':
            return bot.send_message(
                chat_id=self.rule.chat_id,
                audio=file_descriptor,
                caption=caption,
            )
        elif ext == '.ogg':
            return bot.send_voice(
                chat_id=self.rule.chat_id,
                voice=file_descriptor,
                caption=caption,
            )
        else:
            return bot.send_document(
                chat_id=self.rule.chat_id,
                data=file_descriptor,
                caption=caption,
            )

    def send(self, count=1):
        for _i in range(count):
            if not self.state.queue:
                return
            fpath = self.state.queue.pop()
            self.state.failed.append(fpath)
            date = fpath.stat().st_mtime

            with fpath.open('rb') as file_descriptor:
                self._send_file(
                    file_descriptor=file_descriptor,
                    ext=os.path.splitext(str(fpath))[-1],
                    caption=time.strftime('%d.%m.%Y', time.gmtime(date)),
                )
            self.state.sended.append(fpath)
            self.state.failed.pop()


class ChannelsManager:
    channels = None

    def __init__(self, rules=config.RULES, storage_file=config.STORAGE_FILE):
        self.rules = rules
        self.storage_file = storage_file

    def flush(self):
        # flush channels list
        self.channels = []
        for rule in self.rules:
            # init channel
            channel = Channel(rule)
            # flush channel state
            channel.flush()
            # add channel to channels list
            self.channels.append(channel)
        return self.channels

    def read(self):
        # init channels by flush method if storage doesn't exist
        if not os.path.isfile(self.storage_file):
            return self.flush()

        # read states from storage
        with open(config.STORAGE_FILE, 'rb') as f:
            states = pickle.load(f)

        # init all channels
        self.channels = []
        for rule, state in zip(self.rules, states):
            channel = Channel(rule, state)
            self.channels.append(channel)
        return self.channels

    def write(self):
        states = [channel.state for channel in self.channels]
        with open(config.STORAGE_FILE, 'wb') as f:
            pickle.dump(states, f)

    def update(self):
        if not self.channels:
            self.read()
        updated = []
        for channel in self.channels:
            updated.extend(channel.update())
        return updated

    def create_cron_tasks(self):
        if not self.channels:
            self.read()
        for channel in self.channels:
            channel.create_cron_task()

    def send(self):
        if not self.channels:
            self.read()
        for channel in self.channels:
            channel.send()


@contextmanager
def context():
    manager = ChannelsManager()
    manager.read()
    try:
        yield manager
    finally:
        manager.write()
