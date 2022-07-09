from sys import argv
from core import context

aliases = argv[1:]
with context() as channels:
    for channel in channels.channels:
        if not aliases or channel.rule.alias in aliases:
            channel.send()
