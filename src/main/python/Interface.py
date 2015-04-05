from DatabaseHandler import DatabaseHandler
from DotaBetsAnalytics import DotaBetsAnalytics
from DotabuffAdapter import DotabuffAdapter


class Interface:
    def __init__(self, config):
        self.__database_configuration = config['database_configuration']
        self.__spider_configuration = config['spider_configuration']
        self.__import_configuration = config['import_configuration']
        self.__analytics_configuration = config['analytics_configuration']

    def run_import(self):
        update_team = int(self.__import_configuration['update_team'])
        update_opponents = int(self.__import_configuration['update_opponents'])
        teams_id = [int(i) for i in self.__import_configuration['team_id'].split(',')]
        adapter = DotabuffAdapter(self.__database_configuration, self.__spider_configuration)
        for team_id in teams_id:
            try:
                if update_team:
                    adapter.update_team(team_id)
                if update_opponents:
                    adapter.update_opponents(team_id)
                print('Team Updated :: {}'.format(team_id))
            except:
                print('Team Update Failed :: {}'.format(team_id))

    def run_analytics(self):
        method = [str(i) for i in self.__analytics_configuration['method'].split(',')]
        analytics = DotaBetsAnalytics(self.__database_configuration)
        teams_1_id = [int(i) for i in self.__analytics_configuration['team_1_id'].split(',')]
        teams_2_id = [int(i) for i in self.__analytics_configuration['team_2_id'].split(',')]
        team_1_coeff = [float(i) for i in self.__analytics_configuration['team_1_coeff'].split(',')]
        team_2_coeff = [float(i) for i in self.__analytics_configuration['team_2_coeff'].split(',')]

        try:
            len(teams_1_id) == len(teams_2_id) == len(team_1_coeff) == len(team_2_coeff)
            for i in range(len(teams_1_id)):

                if method[0] == 'marginal':
                    if len(method) > 1:
                        last_n_matches = int(method[1])
                    else:
                        last_n_matches = None
                    results = analytics.count_marginal_ev(teams_1_id[i], teams_2_id[i],
                                                          team_1_coeff[i], team_2_coeff[i], last_n_matches)
                    print("\nExpected Bet Multiplication (marginal):\nTeam 1 :: {} ({} matches)"
                          "\nTeam 2 :: {} ({} matches)".format(results[0], results[2], results[1], results[3]))
        except:
            raise ValueError

