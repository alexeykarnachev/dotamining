from DatabaseHandler import DatabaseHandler
from DotabuffSpider import DotabuffSpider
from grab.proxylist import ProxyList


class DotabuffAdapter:
    """
    This class is high level wrapper on DotabuffSpider and DatabaseHandler.
    """
    def __init__(self, db_handler: DatabaseHandler, spider_configuration):
        """
        Constructor for DotabuffAdapter.
        :param db_handler: DatabaseHandler object.
        :param spider_configuration: Dictionary with Spider configuration. Includes keys:
            threads: threads number,
            use_proxy: logical flag to use proxy,
            proxy_file: path to proxy file,
            ignore_id: list or none - matches id to ignore.
        :return:
        """
        self.__db_handler = db_handler
        self.__spider_configuration = spider_configuration

    def __configure_spider(self):
        """
        Private method for DotabuffSpider configuration.
        """
        # Number of threads.
        threads = self.__spider_configuration['threads']
        # Flag to use proxy or not.
        use_proxy = self.__spider_configuration['use_proxy']
        # Proxy file path.
        proxy_file = self.__spider_configuration['proxy_file']
        # Ids to ignore.
        ignore_id = self.__spider_configuration['ignore_id']
        # Spider.
        spider = DotabuffSpider(self.__team_id, ignore_id)

        # Set number of threads.
        spider.thread_number = threads

        # If use proxy...
        if use_proxy:
            # Set proxy list.
            spider.proxylist = ProxyList(proxy_file, source_type='text_file')
            # Set auto change.
            spider.proxy_auto_change = True
            # Enable proxy.
            spider.proxylist_enabled = True

        # Return prepared spider.
        return spider

    def update_team(self, team_id):
        """
        Method to update team in database.
        :param team_id: Team dotabuff id.
        """
        # Get already existing matches id for team.
        self.__ignore_id = self.__db_handler.get_matches_id(team_id)
        self.__team_id = team_id
        # Configure spider.
        spider = self.__configure_spider()
        # Run spider.
        spider.run()
        # Commit spider results.
        self.__db_handler.commit_spider_results(spider.get_results())

    def update_opponents(self, team_id):
        """
        Method to update opponents of specific team.
        """
        for i in self.__db_handler.get_opponents_id(team_id):
            self.update_team(i)


