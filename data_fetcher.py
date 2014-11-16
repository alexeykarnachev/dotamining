# -*- coding: utf-8 -*-

import sqlite3

DB_PATH = 'data/games.db'


class Game(object):
    def __init__(self, fields):
        self.match_id   = fields.get('match_id')
        self.temp_id    = fields.get('temp_id')
        self.date       = fields.get('date')
        self.league     = fields.get('league')
        self.teams      = fields.get('teams')
        self.result     = fields.get('result')
        self.players    = fields.get('players')
        self.prediction = fields.get('prediction')
        self.coeff      = fields.get('coeff')

    def _format_past(self):
        fields = [self.match_id,
                  self.date,
                  self.league,
                  self.result,
                  self.prediction]
        for n in range(2):
            for k in ['name', 'id']:
                fields.append(self.teams[k][n])
        for n in range(10):
            for k in ['name', 'id']:
                fields.append(self.players[k][n])
        s = ','.join(repr(e) for e in fields)
        return s

    def _format_future(self):
        fields = [self.temp_id,
                  self.date,
                  self.league,
                  self.prediction]
        for n in range(2):
            for k in ['name', 'id']:
                fields.append(self.teams[k][n])
        for n in range(2):
            fields.append(self.coeff[n])
        s = ','.join(repr(e) for e in fields)
        return s

    def form(self, fmt):
        if fmt == 'past':
            return self._format_past()
        elif fmt == 'future':
            return self._format_future()


class DatabaseHandler(object):
    def __init__(self):
        self.db_conn = sqlite3.connect(DB_PATH)
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

    def _add_entry(self, table, game):
        prefix = "INSERT INTO {} VALUES (".format(table)
        postfix = ")"

        req = ''.join([prefix, game.form(table), postfix])
        try:
            self.cursor.execute(req)
        except sqlite3.IntegrityError:
            print('Game with same id already exists in {} db!'.format(table))
            return False
        self.db_conn.commit()
        return True

    def _update_table(self):
        pass

    def _read_all_games(self):
        print('Table PAST:')
        self.cursor.execute("SELECT match_id FROM past;")
        print(self.cursor.fetchall())

        print('Table FUTURE:')
        self.cursor.execute("SELECT temp_id FROM future;")
        print(self.cursor.fetchall())

    def __del__(self):
        self.cursor.close()
        self.db_conn.close()


if __name__ == "__main__":
    dh = DatabaseHandler()

    gp = Game({'match_id': 404,
               'date': 'never',
               'league': 'cocksucka league',
               'result': 2,
               'prediction': -1,
               'teams': {
                 'id': [12, 10],
                 'name': ['LGD', 'NewBee']
               },
              'players': {
                'id': range(10),
                'name': ['Noob'] * 10
              }}
             )

    gf = Game({'temp_id': 992,
               'date': 'tomorrow',
               'league': 'shligue',
               'prediction': -1,
               'teams': {
               'id': [34, 10],
               'name': ['NaVi', 'NewBee']
               },
              'coeff': [2.982, 1.413]
              }
              )

    dh._add_entry(table='past', game=gp)
    dh._add_entry(table='future', game=gf)
    dh._read_all_games()