from DatabaseHandler import DatabaseHandler
from DotabuffSpider import DotabuffSpider
from grab.proxylist import ProxyList


class DotabuffAdapter:
    def __init__(self, database_configuration, spider_configuration):
        self.__db_handler = DatabaseHandler(database_configuration)
        self.__spider_configuration = spider_configuration

    def __configure_spider(self):
        threads = int(self.__spider_configuration['threads'])
        use_proxy = int(self.__spider_configuration['use_proxy'])
        proxy_file = self.__spider_configuration['proxy_file']
        spider = DotabuffSpider(self.__team_id, self.__ignore_id)

        spider.thread_number = threads

        if use_proxy:
            spider.proxylist = ProxyList(proxy_file, source_type='text_file')
            spider.proxy_auto_change = True
            spider.proxylist_enabled = True

        return spider

    def update_team(self, team_id):
        self.__ignore_id = self.__db_handler.get_matches_id_by_team_id(team_id)
        self.__team_id = team_id

        spider = self.__configure_spider()
        spider.run()

        self.__db_handler.commit_spider_results(spider.get_results())

    def update_opponents(self, team_id):
        for i in self.__db_handler.get_opponents_id(team_id):
            self.update_team(i)


