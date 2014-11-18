# -*- coding: utf-8 -*-

import os
import csv

CSV_PAST = 'data/past.csv'
CSV_FUTURE = 'data/future.csv'


class Game(object):
    def __init__(self, fields):
        self.fields = fields


class GamePast(Game):
    def __init__(self, fields):
        Game.__init__(fields)

    def as_csv(self):
        fields = [self.fields["match_id"],
                  self.fields["date"],
                  self.fields["league"],
                  self.fields["result"],
                  self.fields["prediction"]]
        for n in range(2):
            for k in ['name', 'id']:
                fields.append(self.fields["teams"][k][n])
        for n in range(10):
            for k in ['name', 'id']:
                fields.append(self.fields["players"][k][n])
        s = ','.join(repr(e) for e in fields)
        return s


class GameFuture(Game):
    def __init__(self, fields):
        Game.__init__(fields)

    def as_csv(self):
        fields = [self.fields["temp_id"],
                  self.fields["date"],
                  self.fields["league"],
                  self.fields["prediction"]]
        for n in range(2):
            for k in ['name', 'id']:
                fields.append(self.fields["teams"][k][n])
        for n in range(2):
            fields.append(self.fields["coeff"][n])
        s = ','.join(repr(e) for e in fields)
        return s


class CSVHandler(object):
    def __init__(self, csv_path=None):
        self.csv_path = csv_path
        self.data = dict()

    def read_csv(self):
        if not os.path.isfile(self.csv_path):
            print('File not found!')

        with open(self.csv_path, newline='', mode='r') as f:
            reader = csv.reader(f, delimiter=',',
                                quoting=csv.QUOTE_NONNUMERIC,
                                quotechar='|')
            self.data = {rows[0]: rows[1] for rows in reader}

    def write_csv(self):
        with open(self.csv_path, 'w', newline='') as f:
            writer = csv.writer(f, delimiter=',')
            for key, value in self.data.items():
                writer.writerow([key, value])


class CSVHandlerPast(CSVHandler):
    def __init__(self, csv_path=None):
        CSVHandler.__init__(csv_path)
        print(self.csv_path)

    @staticmethod
    def get_header():
        hdr = ','.join(
            ["match_id",
             "date",
             "league",
             "result",
             "prediction"]
        )
        for i in range(2):
            hdr = ','.join(
                [hdr,
                 "team{}".format(i),
                 "team{}_id".format(i)]
            )
        for i in range(10):
            hdr = ','.join(
                [hdr,
                 "player{}".format(i),
                 "player{}_id".format(i)]
            )
        return hdr

    def add_entry(self, game):
        if game.fields["match_id"] in self.data['match_id']:
            print('Game with same id already exists in {} db!'.format(
                game.fields["match_id"]))
            return False

        for k in game.fields.keys():
            if k in self.data.keys():
                self.data[k].append(game.fields[k])

    def read_all_games(self):
        print(self.data['match_id'])


    # def _create_table_future(self):
    #     prefix = """CREATE TABLE future ("""
    #     postfix = """);"""
    #     table = ','.join(
    #         ["temp_id integer UNIQUE",
    #          "date text",
    #          "league text",
    #          "prediction integer"]
    #     )
    #     for i in range(2):
    #         table = ','.join(
    #             [table,
    #              "team{} text".format(i),
    #              "team{}_id integer".format(i),
    #              "coeff{} real".format(i)]
    #         )
    #     req = ''.join([prefix, table, postfix])
    #     self.cursor.execute(req)
    #     self.db_conn.commit()


if __name__ == "__main__":
    hp = CSVHandlerPast(CSV_PAST)
    # hf = CSVHandlerFuture(CSV_PAST)

    for iid in range(1, 20, 3):
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

    # gf = Game({'temp_id': 992,
    #            'date': 'tomorrow',
    #            'league': 'shligue',
    #            'prediction': -1,
    #            'teams': {
    #            'id': [34, 10],
    #            'name': ['NaVi', 'NewBee']
    #            },
    #           'coeff': [2.982, 1.413]
    #           }
    #           )

        hp.add_entry(game=gp)
    # dh._add_entry(table='future', game=gf)
    dh._read_all_games()