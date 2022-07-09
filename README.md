# Send File Bot

Telegram bot for sending files to chat or channel by cron.


## Features

* Many file formats
* Send files by cron
* Send files by management commands
* File list updating
* Persistent storage for states
* Statistics
* More than one channels and chats

TODO:

* Permissions
* logging
* manual management by one channel
* tests
* docstrings


## Supported file formats

* Plain text: `.txt`
* Markdown: `.md`
* HTML: `.html`
* Image: `.png`, `.jpg`
* Music: `.mp3`, `.ogg`
* Any other file format will be sent as document.


## Installation

1. Clone or download project
2. `cp config{_example,}.py`
3. Edit config.py
4. Place your files to `path`.
5. add cron tasks.


## Usage

Run management interface:

```bash
python3 update.py
```

Send file (you can create cron task for it):

```bash
python3 send.py "channel alias"
```

Or send files to all channels:

```bash
python3 send.py
```
