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
        method = self.__analytics_configuration['method']
        analytics = DotaBetsAnalytics(self.__database_configuration, self.__analytics_configuration)

        if method == 'marginal':
            results = analytics.count_marginal_ev()
            print("\nExpected Bet Multiplication (marginal):\nTeam 1 :: {} ({} matches)"
                  "\nTeam 2 :: {} ({} matches)".format(results[0], results[2], results[1], results[3]))