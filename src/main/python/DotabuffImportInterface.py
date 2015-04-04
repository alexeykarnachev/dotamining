from DotabuffAdapter import DotabuffAdapter


class Interface:
    def __init__(self, config):
        self.__database_configuration = config['database_configuration']
        self.__spider_configuration = config['spider_configuration']
        self.__import_configuration = config['import_configuration']

    def run_import(self):
        update_team = int(self.__import_configuration['update_team'])
        update_opponents = int(self.__import_configuration['update_opponents'])
        team_id = int(self.__import_configuration['team_id'])
        adapter = DotabuffAdapter(self.__database_configuration, self.__spider_configuration)

        if update_team:
            adapter.update_team(team_id)
        if update_opponents:
            adapter.update_opponents(team_id)
