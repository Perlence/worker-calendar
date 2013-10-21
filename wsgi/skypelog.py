# -*- encoding: utf-8 -*-
import re
import string
import calendar
import itertools
from collections import Counter, namedtuple
from datetime import datetime

RUSSIAN = u'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

MEMBERS = [
    'ramzesp1989',
    'nelasork',
    'crossaidi',
    'jouki_nebov',
    'khaimenova_evgeniya',
    'sacret.nk',
    'mnogabykv',
    'zetsuboulizzy',
    'moozee_',
    'dust.harvesting',
]

def grouper(iterable, n, fillvalue=None):
    '''Collect data into fixed-length chunks or blocks

    >>> list(grouper('ABCDEFG', 3, 'x'))
    [('A', 'B', 'C'), ('D', 'E', 'F'), ('G', 'x', 'x')]
    '''
    args = [iter(iterable)] * n
    return itertools.izip_longest(fillvalue=fillvalue, *args)

class Range(object):
    def __init__(self, *args):
        s = slice(*args)
        self.start = s.start
        self.stop  = s.stop

    def __eq__(self, other):
        if self.start and self.stop:
            return self.start <= other < self.stop
        elif self.start:
            return self.start <= other
        else:
            return other < self.stop


class Message(namedtuple('Message', 'timestamp, author, body, crc')):
    MESSAGE_FMT = u'{crc:010} [{timestamp:%d.%m.%Y %H:%M:%S}] {author}: {body}'

    def language(self):
        languages = Counter(russian=0, english=0)
        for char in self.body:
            if char in string.lowercase:
                languages['english'] += 1
            elif char in RUSSIAN:
                languages['russian'] += 1
        return languages.most_common(1)[0][0]

    def isLink(self):
        return ('http://' in self.body or 
                'www.' in self.body)

    def __hash__(self):
        return self.crc

    def __eq__(self, other):
        return self.crc == other.crc

    def __str__(self):
        return self.MESSAGE_FMT.format(**self._asdict())


class SkypeLog(object):
    re_timestamp = re.compile(r'(\d+) \[(\d+\.\d+\.\d+ \d+:\d+:\d+)\] ([^:]+): ')

    def __init__(self):
        self.messages = set()

    def load(self, fp, encoding='utf-8'):
        if isinstance(fp, str):
            f = open(fp, 'r')
        elif isinstance(fp, file):
            f = fp
        self.contents = f.read().decode(encoding)
        self.parse(self.contents)

    def insort(self, message):
        self.messages.add(message)

    def parse(self, log):
        messages = self.re_timestamp.split(log)[1:]
        for crc, timestamp, author, body in grouper(messages, 4):
            timestampobj = datetime.strptime(timestamp, '%d.%m.%Y %H:%M:%S')
            message = Message(timestampobj, author, body.rstrip('\n'), int(crc))
            self.insort(message)

    def querydate(self, year=None, month=None, day=None):
        def parsequery(s, default=None):
            if not s:
                return default
            result = []
            for x in s.strip(',').split(','):
                if '-' in x:
                    parts = x.split('-', 1)
                    start = int(parts[0]) if parts[0] else None
                    end = int(parts[1]) + 1 if parts[1] else None
                    result.append(Range(start, end))
                else:
                    result.append(int(x.strip(' ')))
            return result

        if year is None and month is None and day is None:
            return sorted(self.messages)

        year = parsequery(year, [datetime.today().year])
        month = parsequery(month, [datetime.today().month])
        day = parsequery(day, None)

        result = []
        for message in self.messages:
            if (message.timestamp.year in year and
                message.timestamp.month in month):
                    if day:
                        if message.timestamp.day in day:
                            result.append(message)
                    else:
                        result.append(message)
        return sorted(result)


def dialogue(messages):
    days_russian, days_english = [0] * 31, [0] * 31
    array = [['Day', 'Russian', 'English']]
    grouped = itertools.groupby(messages, lambda x: x.timestamp.day)
    for day, day_messages in grouped:
        day_messages = list(day_messages)
        days_russian[day - 1] = len(filter(lambda x: x.language() == 'russian', day_messages))
        days_english[day - 1] = len(filter(lambda x: x.language() == 'english', day_messages))

    for d, r, e in zip(range(1, 32), days_russian, days_english):
        array += [[str(d), r, e]]
    pprint.pprint(array)

def club(messages, groupby='week'):
    if groupby == 'day' or groupby is None:
        keyfunc = lambda x: x.timestamp.day
    elif groupby == 'week':
        keyfunc = lambda x: x.timestamp.timetuple().tm_yday / 7
    elif groupby == 'month':
        keyfunc = lambda x: x.timestamp.month
    elif groupby == 'year':
        keyfunc = lambda x: x.timestamp.year

    result = []
    grouped = itertools.groupby(messages, keyfunc)
    for day, day_messages in grouped:
        day_messages = list(day_messages)
        timestamp = day_messages[0].timestamp
        # Skip weekends
        if timestamp.timetuple().tm_wday < 5:
            members = [filter(lambda x: x.author == m, day_messages) for m in MEMBERS]
            result += [['{:%d %B}'.format(timestamp)] + map(len, members)]
    return result
