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
#                    'result': 2,
#                    'prediction': -1,
#                    'teams': {
#                      'id': [12, 10],
#                      'name': ['LGD', 'NewBee']
#                    },
#                   'players': {
#                     'id': list(range(10)),
#                     'name': ['Noob'] * 10
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
