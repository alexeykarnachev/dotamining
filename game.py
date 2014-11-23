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
                  self.fields["region"],
                  self.fields["result"],
                  self.fields["prediction"]]
        for k in ['name', 'id']:
            fields.append(self.fields["team_radiant"][k][0])
        for k in ['name', 'id']:
            fields.append(self.fields["team_dire"][k][1])
        for n in range(5):
            for k in ['name', 'id']:
                fields.append(self.fields["players_radiant"][k][n])
        for n in range(5):
            for k in ['name', 'id']:
                fields.append(self.fields["players_dire"][k][n])
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