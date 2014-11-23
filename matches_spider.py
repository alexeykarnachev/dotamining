from grab.proxylist import ProxyList, SOURCE_LIST
from grab.spider import Spider, Task
from parse_routines import *
import re


class TeamsIdSpider(Spider):
    initial_urls = ['http://www.dotabuff.com/esports/teams']
    matches_ids = set()

    def prepare(self):
        # TODO: DB connection
        return

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
        match_id = \
            parse_game_object_from_match_page_grab(grab)
        self.matches_ids.add(match_id)
        print(len(self.matches_ids))


if __name__ == '__main__':
    bot = TeamsIdSpider(
        thread_number=1,
        priority_mode='const')
    #bot.proxylist = ProxyList('D:/proxy.txt', source_type='text_file')
    #bot.proxy_auto_change = True
    #bot.proxylist_enabled = False
    try:
        bot.run()
    except KeyboardInterrupt:
        pass

