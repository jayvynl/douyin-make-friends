import itertools
import sqlite3
import typing

import settings

conn = sqlite3.connect(settings.DB_FILE)
c = conn.cursor()
c.execute(
    'CREATE TABLE IF NOT EXISTS user'
    '(name text, sent boolean default FALSE)'
)
c.execute(
    'CREATE TABLE IF NOT EXISTS video'
    '(name text)'
)
conn.commit()


def save_user(name: typing.Union[str, typing.Sequence[str]]) -> None:
    if isinstance(name, str):
        name = [name]
    c.execute(
        'INSERT INTO user(name) VALUES ' +
        ','.join(itertools.repeat('(?)', len(name))),
        name
    )
    conn.commit()


def save_video(name: typing.Union[str, typing.Sequence[str]]) -> None:
    if isinstance(name, str):
        name = [name]
    c.execute(
        'INSERT INTO video(name) VALUES ' +
        ','.join(itertools.repeat('(?)', len(name))),
        name
    )
    conn.commit()


def update(names: typing.Sequence[str]) -> None:
    c.execute(
        'UPDATE user SET sent=TRUE WHERE name IN ({})'.format(
            ','.join(itertools.repeat('?', len(names)))),
        names
    )
    conn.commit()


def users(all_: bool = True) -> typing.Generator[str, None, None]:
    sql = 'SELECT name FROM user'
    if not all_:
        sql += ' WHERE sent=FALSE'
    c.execute(sql)
    return (o[0] for o in c.fetchall())


def videos() -> typing.Generator[str, None, None]:
    sql = 'SELECT name FROM video'
    c.execute(sql)
    return (o[0] for o in c.fetchall())
