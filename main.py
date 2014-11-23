# -*- coding: utf-8 -*-
#
#

from game import *


# if __name__ == "__main__":
#     dh = DatabaseHandler()
#
#     for idx in range(10 ** 5):
#         gp = GamePast({'match_id': idx,
#                    'date': 'never',
#                    'league': 'cocksucka league',
#                    'region': 'china',
#                    'result': 2,
#                    'prediction': -1,
#                    'team_radiant': {
#                      'id': [12],
#                      'name': ['LGD']
#                    },
#                    'team_dire': {
#                      'id': [10],
#                      'name': ['ES']
#                    },
#                   'players_radiant': {
#                     'id': list(range(5)),
#                     'name': ['Noob'] * 5
#                   },
#                   'players_dire': {
#                     'id': list(range(5)),
#                     'name': ['Noob2'] * 5
#                   }}
#                  )
#
#         gf = GameFuture({'temp_id': idx,
#                    'date': 'tomorrow',
#                    'league': 'shligue',
#                    'prediction': -1,
#                    'teams': {
#                    'id': [34, 10],
#                    'name': ['NaVi', 'NewBee']
#                    },
#                   'coeff': [2.982, 1.413]
#                   }
#                   )
#
#         dh.add_entry(table='past', game=gp)
#         dh.add_entry(table='future', game=gf)
#         if not idx % 1000:
#             print(idx)
# #    dh._read_all_games()
