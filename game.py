# -*- coding: utf-8 -*-
#
#


class Game(object):
    def __init__(self, fields):
        self.fields = fields


class GamePast(Game):
    def __init__(self, fields):
        super().__init__(fields)

    def as_str(self):
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
        super().__init__(fields)

    def as_str(self):
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