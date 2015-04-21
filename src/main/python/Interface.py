import datetime
import pickle
from numpy.ma import cumsum
from pandas import DataFrame
from scipy.sparse import triu
from scipy.sparse.csgraph._traversal import connected_components
from DatabaseHandler import DatabaseHandler
from DotaBetsAnalytics import DotaBetsAnalytics
from DotabuffAdapter import DotabuffAdapter
import networkx as nx
import matplotlib.pyplot as plt
from config import *
import scipy as sp
import numpy as np


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

    def run_backtesting(self, dates, window, coeff_functions):
        start_date = dates[0]
        end_date = dates[1]
        old_day = datetime.datetime(2010, 1, 1)
        one_day = datetime.timedelta(days=1)
        days_window = datetime.timedelta(days=window)
        days = (end_date - start_date).days
        banks = {}
        for day in range(days):
            print(day, range(days))
            today = start_date + datetime.timedelta(days=day)
            try:
                test_analytics = DotaBetsAnalytics(self.__db_handler.import_network([today, today + one_day], [0, 1]))
                learn_analytics = DotaBetsAnalytics(self.__db_handler.import_network([today - days_window, today]))
                bookmaker_analytics = DotaBetsAnalytics(self.__db_handler.import_network([old_day, today]))
            except:
                continue

            teams_list = test_analytics.graph.edges()
            teams_analyzed = []
            for teams in teams_list:
                if (teams in teams_analyzed) or (teams[1], teams[0]) in teams_analyzed:
                    continue
                else:
                    teams_analyzed.append(teams)
                    try:
                        bookmaker_winrate = bookmaker_analytics.marginal_winrate(teams)

                        if bookmaker_winrate[0] >= bookmaker_winrate[1]:
                            fav = 0
                            out = 1
                        else:
                            fav = 1
                            out = 0

                        true_result = test_analytics.joint_winrate((teams[fav], teams[out]))
                        coeff = [coeff_functions[0](bookmaker_winrate[fav]), coeff_functions[1](bookmaker_winrate[out])]

                        methods = [learn_analytics.marginal_winrate,
                                   learn_analytics.joint_winrate,
                                   learn_analytics.neighbors_winrate]

                        for method_ind in range(len(methods)):
                            method_winrate = methods[method_ind]((teams[fav], teams[out]))
                            ev = [coeff[0] * method_winrate[0], coeff[1] * method_winrate[1]]

                            if ev[0] >= ev[1]:
                                ev_fav = 0
                                ev_out = 1
                            else:
                                ev_fav = 1
                                ev_out = 0

                            if ev[ev_fav] >= 0:
                                actual_won = (coeff[ev_fav] * true_result[ev_fav]) - 1
                                ev_won = ev[ev_fav] - 1
                                fav_won = (coeff[0] * true_result[0]) - 1
                                out_won = (coeff[1] * true_result[1]) - 1
                                result_row = [actual_won, ev_won, fav_won, out_won]
                                if method_ind not in banks:
                                    banks[method_ind] = DataFrame(columns=('actual', 'ev', 'fav', 'out'))

                                banks[method_ind].loc[len(banks[method_ind])] = result_row
                    except:
                        continue

        for bank in banks:
            banks[bank].cumsum(0).plot()
            plt.show()

if __name__ == '__main__':
    I = Interface(CON_PATH)
    I.run_backtesting(dates=[datetime.datetime(2014, 12, 1), datetime.datetime(2015, 1, 1)], window=15,
                      coeff_functions=[lambda x: 1.3, lambda x: 2.4])







