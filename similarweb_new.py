import json
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from country import const_countries

# TODO проверка на капчу
# TODO красивые цифры как на симиларе
# TODO запись в файл csv ?
# TODO плохие домены чекать через селениум
# TODO проверка инпут файла на https / www / .
# TODO добавить описание функций и класов
# TODO посмотреть, что можно взять из предыдущей версии симилара


class Similar:

    def __init__(self, headless=True):
        if headless:
            self.options = webdriver.ChromeOptions()
            self.options.add_argument('headless')
            self.driver = webdriver.Chrome(chrome_options=self.options)
        else:
            self.driver = webdriver.Chrome()
        self.file_input = 'input.txt'
        self.domain = []
        self.count = 0

    def __create_list_of_domains(self):
        with open(file=self.file_input, mode='r', encoding='utf-8') as file:
            for url in file:
                url = url.replace('\n', '')
                self.domain.append(url)

    def run(self):
        self.__create_list_of_domains()
        while True:
            if self.count == len(self.domain):
                self.driver.quit()
                break
            self.count += 1
            self.driver.get(f'https://data.similarweb.com/api/v1/data?domain={self.domain[self.count - 1]}')
            source = self.driver.page_source
            soup = BeautifulSoup(source, 'html.parser')

            print(soup)  # убрать после отладки

            if 'HTTP ERROR 429' in str(soup) or '<html><head></head><body></body></html>' in str(soup):
                print('Забанили, нужно подождать')
                time.sleep(61)
                self.count -= 1
            elif '{}' in str(soup):
                print('https://www.similarweb.com/website/' + str(self.domain[self.count - 1]))
            elif 'invalid payload' in str(soup):
                print('Это не домен! Проверь - ' + str(self.domain[self.count - 1]))
            else:
                find_json = soup.find('pre').text
                _json = json.loads(find_json)
                monthly_visits_top5 = _json['EstimatedMonthlyVisits']
                top_country = _json['TopCountryShares']
                site_name = _json['SiteName']
                monthly_visits = []
                if self.domain[self.count - 1] == site_name:
                    for date in monthly_visits_top5:
                        monthly_visits.append(monthly_visits_top5[date])
                        print(site_name, date, monthly_visits_top5[date])

                    print(site_name + '\t' + 'Total Traffic' + '\t' + str(monthly_visits[-1]))

                    for country in top_country:
                        print(site_name, const_countries[str(country['Country'])], round(monthly_visits[-1] * country['Value']))
                else:
                    print('https://www.similarweb.com/website/' + str(self.domain[self.count - 1]))


if __name__ == '__main__':
    similar = Similar(headless=False)  # Если False - браузер будет виден, если True - не будет
    similar.run()
