# -*- coding: utf-8 -*-
#
#

import sqlite3
import config


class DatabaseHandler(object):
    def __init__(self):
        self.db_conn = sqlite3.connect(config.DB_PATH)
        self.cursor = self.db_conn.cursor()

        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [e[0] for e in self.cursor.fetchall()]
        if 'past' not in tables:
            self._create_table_past()
        if 'future' not in tables:
            self._create_table_future()

    def _create_table_past(self):
        prefix = """CREATE TABLE past ("""
        postfix = """);"""
        table = ','.join(
            ["match_id integer UNIQUE",
             "date text",
             "league text",
             "result integer",
             "prediction integer"]
        )
        for i in range(2):
            table = ','.join(
                [table,
                 "team{} text".format(i),
                 "team{}_id integer".format(i)]
            )
        for i in range(10):
            table = ','.join(
                [table,
                 "player{} text".format(i),
                 "player{}_id integer".format(i)]
            )
        req = ''.join([prefix, table, postfix])
        self.cursor.execute(req)
        self.db_conn.commit()

    def _create_table_future(self):
        prefix = """CREATE TABLE future ("""
        postfix = """);"""
        table = ','.join(
            ["temp_id integer UNIQUE",
             "date text",
             "league text",
             "prediction integer"]
        )
        for i in range(2):
            table = ','.join(
                [table,
                 "team{} text".format(i),
                 "team{}_id integer".format(i),
                 "coeff{} real".format(i)]
            )
        req = ''.join([prefix, table, postfix])
        self.cursor.execute(req)
        self.db_conn.commit()

    def add_entry(self, table, game):
        prefix = "INSERT INTO {} VALUES (".format(table)
        postfix = ")"

        req = ''.join([prefix, game.as_str(), postfix])
        try:
            self.cursor.execute(req)
        except sqlite3.IntegrityError:
            print('Game with id already exists in {} db!'.format(table))
            return False
        return True

    def read_all_games(self):
        print('Table PAST:')
        self.cursor.execute("SELECT match_id FROM past;")
        print(self.cursor.fetchall())

        print('Table FUTURE:')
        self.cursor.execute("SELECT temp_id FROM future;")
        print(self.cursor.fetchall())

    def __del__(self):
        self.db_conn.commit()
        self.cursor.close()
        self.db_conn.close()
