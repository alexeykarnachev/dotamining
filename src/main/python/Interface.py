import datetime
from pandas import DataFrame
from DatabaseHandler import DatabaseHandler
from DotaBetsAnalytics import DotaBetsAnalytics
from DotabuffAdapter import DotabuffAdapter
import matplotlib.pyplot as plt
from config import *
import pandas as pd
from random import randint


class Interface:
    """
    This class is high level interface, which combining data obtaining and analytics.
    """

    def __init__(self, con_path):
        self.__db_handler = DatabaseHandler(con_path)

    def run_update(self, teams_to_update, threads, use_proxy, proxy_file, update_opponents):
        for team_id in teams_to_update:
            spider_configuration = {'threads': threads,
                                    'use_proxy': use_proxy,
                                    'proxy_file': proxy_file,
                                    'ignore_id': self.__db_handler.get_matches_id(team_id)}
            adapter = DotabuffAdapter(self.__db_handler, spider_configuration)
            adapter.update_team(team_id)
            print('Team Updated :: {}'.format(team_id))
            if update_opponents:
                adapter.update_opponents(team_id)
                print('Team Opponents Updated :: {}'.format(team_id))

    def run_backtesting(self, dotalounge_hist_file, dotalounge_names_file, window):
        dotalounge_hist = pd.DataFrame.from_csv(dotalounge_hist_file, header=None)
        dotalounge_names = pd.DataFrame.from_csv(dotalounge_names_file, header=0, index_col=None)
        names = dotalounge_names['names'].tolist()
        index = dotalounge_names['id'].tolist()
        delta = datetime.timedelta(days=window)
        BANKS = {}
        unique_dates = list(set(dotalounge_hist.ix[:, 6].tolist()))
        i = 0
        for date_str in unique_dates:
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            games = dotalounge_hist.loc[(dotalounge_hist.ix[:, 6] == date_str)]
            dates = [date - delta, date]
            analytics = DotaBetsAnalytics(self.__db_handler.import_network(dates=dates))
            methods = [analytics.marginal_winrate,
                       analytics.joint_winrate,
                       analytics.neighbors_winrate]

            for game in games.iterrows():
                teams_names = [game[1][1], game[1][2]]

                if teams_names[0] in names and teams_names[1] in names:
                    try:
                        teams_id = [index[names.index(teams_names[0])], index[names.index(teams_names[1])]]
                        result = [0, 0]
                        result[game[1][3]] = 1
                        coeff = [game[1][4], game[1][5]]

                        probabilities = [result[0]]
                        for method_ind in range(len(methods)):
                            method_winrate = methods[method_ind](teams_id)
                            probabilities += [method_winrate[0], method_winrate[1]]
                            evs = [coeff[0] * method_winrate[0] - 1, coeff[1] * method_winrate[1] - 1]

                            rand_fav = randint(0, 1)
                            rand_out = abs(rand_fav - 1)
                            rand_won = result[rand_fav] * coeff[rand_fav] - 1

                            vs_book_fav = 0 if coeff[0] >= coeff[1] else 1
                            vs_book_out = abs(vs_book_fav - 1)
                            vs_book_won = result[vs_book_fav] * coeff[vs_book_fav] - 1

                            best_fav = 0 if result[0] == 1 else 1
                            best_won = result[best_fav] * coeff[best_fav] - 1

                            book_fav = 0 if coeff[0] <= coeff[1] else 1
                            book_out = abs(book_fav - 1)
                            book_won = result[book_fav] * coeff[book_fav] - 1

                            my_fav = 0 if evs[0] >= evs[1] else 1
                            my_out = abs(my_fav - 1)

                            if evs[my_fav] >= 0 and evs[my_out] < 0:
                                my_won = result[my_fav] * coeff[my_fav] - 1
                                my_ev = evs[my_fav]
                            else:
                                my_won = 0
                                my_ev = 0

                            if method_ind not in BANKS:
                                BANKS[method_ind] = DataFrame(columns=('rand_won',
                                                                       'vs_book_won',
                                                                       'book_won',
                                                                       'my_won'))
                            result_row = [rand_won, vs_book_won, book_won, my_won]
                            BANKS[method_ind].loc[len(BANKS[method_ind])] = result_row

                    except:
                        pass

            i += 1
            print(i, len(unique_dates))

        for bank in BANKS:
            BANKS[bank].cumsum(0).plot()
            plt.show()

    def run_analytics(self, teams_list, coeffs_list, window):
        delta = datetime.timedelta(days=window)
        today = datetime.date.today()
        dates = [today - delta, today]
        analytics = DotaBetsAnalytics(self.__db_handler.import_network(dates=dates))

        for i in range(len(teams_list)):
            results = DataFrame(columns=['1', '2'])
            teams = teams_list[i]
            coeffs = coeffs_list[i]

            try:
                marginal_winrates = analytics.marginal_winrate(teams)
                results.loc[len(results)] = [(marginal_winrates[0] * coeffs[0] - 1), (marginal_winrates[1] * coeffs[1] - 1)]
            except:
                results.loc[len(results)] = [-100, -100]

            try:
                joint_winrates = analytics.joint_winrate(teams)
                results.loc[len(results)] = [(joint_winrates[0] * coeffs[0] - 1), (joint_winrates[1] * coeffs[1] - 1)]
            except:
                results.loc[len(results)] = [-100, -100]

            try:
                neighbors_winrates = analytics.neighbors_winrate(teams)
                results.loc[len(results)] = [(neighbors_winrates[0] * coeffs[0] - 1), (neighbors_winrates[1] * coeffs[1] - 1)]
            except:
                results.loc[len(results)] = [-100, -100]

            print('{} VS {}'.format(teams[0], teams[1]))
            print(results)


if __name__ == '__main__':
    I = Interface(CON_PATH)

    # I.run_backtesting(dotalounge_hist_file='c:/workspace/projects/dotamining/ext/dotalounge_hist.csv',
    #                   dotalounge_names_file='c:/workspace/projects/dotamining/ext/dotalounge_names.csv',
    #                   window=120)

    I.run_analytics([(1333179, 1820360), (1966890, 726228), (111474, 5), (543897, 2224197), (1513164, 1161668)],
                    [(1.2, 4.7), (8.9, 1.1), (3.3, 1.4), (1.5, 2.8), (1.8, 2.2)],
                    120)






