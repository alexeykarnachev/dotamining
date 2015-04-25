import re
import datetime
from grab import Grab
from bs4 import BeautifulSoup as bs
import pandas as pd


class DotaloungeParser():
    def __init__(self):
        self.__g = Grab()

    def __parse_match_grab(self, match_grab):
        soup = bs(match_grab.doc.body)
        box = soup.find('div', {'class': 'box-shiny-alt'})

        date_text = box.find('div', {'style': 'display: flex'}).text
        if 'hour' in date_text:
            delta = datetime.timedelta(days=1)
        elif 'day' in date_text:
            days = int(re.findall(re.compile('(\d+) day'), date_text)[0])
            delta = datetime.timedelta(days=days+1)
        elif 'month' in date_text:
            months = int(re.findall(re.compile('(\d+) month'), date_text)[0])
            delta = datetime.timedelta(days=months*31+31)
        elif 'year' in date_text:
            years = int(re.findall(re.compile('(\d+) year'), date_text)[0])
            delta = datetime.timedelta(days=years*365+365)

        date = datetime.date.today() - delta

        teams = [re.sub(' ', '', i.text) for i in box.find_all('b')]
        result = [bool(re.match(re.compile('.+\(win\)'), i)) for i in teams].index(True)
        teams[result] = re.sub(re.compile('\(win\)'), '', teams[result])

        coeff_box = box.find('div', {'class': 'full'})
        coeff_text = re.sub('0 for 0', '', coeff_box.text)

        value_re = re.compile('.?Value([-+]?\d*\.\d+|\d+) for 1')
        coeff = [str(1 + float(i)) for i in re.findall(value_re, coeff_text)]

        row = ','.join(teams) + ',' + str(result) + ',' + ','.join(coeff) + ',' + str(date) + '\n'

        return row

    def parse_matches(self, csv_path, matches_id=list(range(5000, 6401))):
        with open(csv_path, 'w') as f:
            for match_id in matches_id:
                self.__g.go('http://dota2lounge.com/match?m=' + str(match_id))
                try:
                    row = self.__parse_match_grab(self.__g)
                    f.write(str(match_id) + ',' + row)
                    print(str(match_id) + ',' + row)
                except:
                    pass
            f.close()


# if __name__ == '__main__':
#     parser = DotaloungeParser()
#     parser.parse_matches('c:/workspace/projects/dotamining/ext/dotalounge_hist.csv')
#     df = pd.DataFrame.from_csv('c:/workspace/projects/dotamining/ext/dotalounge_hist.csv', header=None)
#
#     names = pd.DataFrame(columns=['names'])
#     names['names'] = (list(set(df.ix[:, 1].tolist()) & set(df.ix[:, 2].tolist())))
#     names.to_csv('c:/workspace/projects/dotamining/ext/dotalounge_names.csv')

