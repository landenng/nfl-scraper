import time
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver import Chrome
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By

def main():
    opt = webdriver.ChromeOptions()
    opt.add_argument('--headless')
    opt.page_load_strategy = 'none'

    driver = Chrome(options = opt)
    driver.implicitly_wait(1)

    urls = [
            'https://www.espn.com/nfl/stats/player/_/view/offense#',
            'https://www.espn.com/nfl/stats/player/_/stat/rushing',
            'https://www.espn.com/nfl/stats/player/_/stat/receiving',
            'https://www.espn.com/nfl/stats/player/_/view/defense',
            'https://www.espn.com/nfl/stats/player/_/view/special',
            'https://www.espn.com/nfl/stats/player/_/view/special/stat/kicking',
            'https://www.espn.com/nfl/stats/player/_/view/special/stat/punting'
            ]

    col_dict = { 
                'offense_passing':   [ 'Name', 'Team', 'POS', 'GP', 'CMP', 'ATT', 'CMP%', 'YDS', 'AVG', 'YDS/G', 'LNG', 'TD', 'INT', 'SACK', 'SYL', 'QBR', 'RTG' ],
                'offense_rushing':   [ 'Name', 'Team', 'POS', 'GP', 'ATT', 'YDS', 'AVG', 'LNG', 'BIG', 'TD', 'YDS/G', 'FUM', 'LST', 'FD' ], 
                'offense_receiving': [ 'Name', 'Team', 'POS', 'GP', 'REC', 'TGTS', 'YDS', 'AVG', 'TD', 'LNG', 'BIG', 'YDS/G', 'FUM', 'LST', 'YAC', 'FD' ],
                'defense':           [ 'Name', 'Team', 'POS', 'GP', 'SOLO', 'AST', 'TOT', 'SACK', 'YDS', 'TFL', 'PD', 'INT', 'YDS', 'LNG', 'TD', 'FF', 'FR', 'FTD' ],
                'special_returning': [ 'Name', 'Team', 'POS', 'GP', 'ATT', 'YDS', 'AVG', 'LNG', 'TD', 'ATT', 'YDS', 'AVG', 'LNG', 'TD', 'FC' ],
                'special_kicking':   [ 'Name', 'Team', 'POS', 'GP', 'FGM', 'FGA', 'FG%', 'LNG', '1-19', '20-29', '30-39', '40-49', '50+', 'XPM', 'XPA', 'XP%' ],
                'special_punting':   [ 'Name', 'Team', 'POS', 'GP', 'PUNTS', 'YDS', 'LNG', 'AVG', 'NET', 'PBLK', 'IN20', 'TB', 'FC', 'ATT', 'YDS', 'AVG' ]
                }

    for i in range(len(urls)):
        load_page(driver, urls[i])

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        stats = get_stats(col_dict, list(col_dict)[i], soup)

        get_csv(stats, col_dict, i)

def load_page(driver: webdriver.Chrome, url: str) -> None:
    driver.get(url)
    time.sleep(1)
    while True:
        time.sleep(1)
        try:
            btn = driver.find_element(By.XPATH, '//a[@class="AnchorLink loadMore__link"]')
            btn.click()
        except NoSuchElementException:
            break

def get_stats(d: dict, k: str, soup: BeautifulSoup) -> list:
    tables = soup.find_all('tbody', 'Table__TBODY')
    players = tables[0].find_all('tr', 'Table__TR Table__TR--sm Table__even')
    stats = tables[1].find_all('tr', 'Table__TR Table__TR--sm Table__even')
    data = [ [] for _ in range(len(d[k])) ]
    for player in players:
        player_names = player.find_all('a', 'AnchorLink')
        player_teams = player.find_all('span', 'pl2 ns10 athleteCell__teamAbbrev')
        for player_name in player_names:
            data[0].append(player_name.string)
        for player_team in player_teams:
            data[1].append(player_team.string)
    for stat in stats:
        player_stats = stat.find_all('td', 'Table__TD')
        for i in range(2, len(d[k])):
            if i - 2 == 0: data[i].append(player_stats[i - 2].string)
            else: data[i].append((str(player_stats[i - 2].string).replace(',', '')))
    return list(zip(*data))

def get_csv(stats: list, cols: dict, i: int) -> None:
    print()
    print('-' * 120)
    print(list(cols)[i].upper())
    df = pd.DataFrame(stats, columns = list(cols.values())[i])
    df.index.name = 'RK'
    df.index += 1
    print(df)
    print('-' * 120)
    df.to_csv(f'./data/{list(cols)[i]}.csv')

if __name__ == '__main__':
    main()
