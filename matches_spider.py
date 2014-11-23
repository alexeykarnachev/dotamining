from grab.proxylist import ProxyList, SOURCE_LIST
from grab.spider import Spider, Task
from handler_sql import DatabaseHandler
from parse_routines import *
import re


class TeamsIdSpider(Spider):
    initial_urls = ['http://www.dotabuff.com/esports/teams']
    new_matches_urls = set()
    parsed_matches_urls = set()

    def prepare(self):
        dh = DatabaseHandler()

    def task_initial(self, grab, task):
        teams_matches_pages_urls = \
            get_teams_matches_pages_urls_from_teams_page_grab(grab)

        for team_matches_page_url in teams_matches_pages_urls:
            yield Task('matches_pages', url=team_matches_page_url)

    def task_matches_pages(self, grab, task):
        matches_pages_urls = \
            get_matches_pages_urls_from_matches_page_grab(grab)

        for matches_page_url in matches_pages_urls:
            yield Task('matches_single_pages', url=matches_page_url)

    def task_matches_single_pages(self, grab, task):
        valid_matches_urls = \
            get_valid_matches_urls_from_matches_page_grab(grab)

        for matches_page_url in valid_matches_urls:
            yield Task('match_details', url=matches_page_url)

    def task_match_details(self, grab, task):
        if self.parsed_matches_urls.isdisjoint(list([task.url])):
            gp = parse_game_object_from_match_page_grab(grab)
            self.parsed_matches_urls.add(task.url)

        print(len(self.matches_ids))


class TeamsIdSpiderWriter(TeamsIdSpider):
    def __init__(self, path_to_db, path_to_proxies, source_type,
                 proxylist_enabled, proxy_auto_change,
                 thread_number, priority_mode):
        super().__init__()
        self.path_to_db = path_to_db
        self.proxylist_enabled = proxylist_enabled
        self.proxy_auto_change = proxy_auto_change
        self.thread_number = thread_number
        self.priority_mode = priority_mode
        if proxylist_enabled:
            self.proxylist = ProxyList(path_to_proxies, source_type)

if __name__ == '__main__':
    bot = TeamsIdSpiderWriter(path_to_db="", path_to_proxies="",
                              source_type="text_file", proxylist_enabled=False,
                              proxy_auto_change=False,
                              thread_number=10, priority_mode="const")
    # bot.proxylist = ProxyList('D:/proxy.txt', source_type='text_file')
    #bot.proxy_auto_change = True
    #bot.proxylist_enabled = False
    try:
        bot.run()
    except KeyboardInterrupt:
            pass

