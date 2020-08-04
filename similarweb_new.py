import json
import time
from selenium import webdriver
from bs4 import BeautifulSoup
from country import const_countries

# TODO проверка на капчу

# TODO запись в файл csv ?
# TODO плохие домены чекать через селениум

# TODO посмотреть, что можно взять из предыдущей версии симилара
# TODO проверка на наличие хромдрайвера


class Similar:
    """ Класс для работы с API Similarweb. """

    def __init__(self, headless=True):
        """ Параметры нужные для работы. """
        if headless:
            self.options = webdriver.ChromeOptions()
            self.options.add_argument('headless')
            self.driver = webdriver.Chrome(chrome_options=self.options)
        else:
            self.driver = webdriver.Chrome()
        self.file_input = 'input.txt'
        self.domain = []
        self.monthly_visits = []
        self.count = 0

    def __create_list_of_domains(self):
        """ Создание чистого списка доменов из файла. """
        with open(file=self.file_input, mode='r', encoding='utf-8') as file:
            for url in file:
                url = url.replace('\n', '')
                if '//' in url:
                    need_url = url.replace('http://', '').replace('https://', '').replace('www.', '').split('/')[0]
                    self.domain.append(need_url)
                else:
                    need_url = url.replace('www.', '')
                    self.domain.append(need_url)

    def __rounding(self, number_to_round):
        """ Округление трафика, к виду similar'a. """
        number = str(number_to_round)
        if len(number) >= 7:
            h = number[:3] + '.' + number[3:]
            j = round(float(h))
            g = str(j) + '0' * (len(number) - 3)
            return g
        elif 5 <= len(number) <= 6:
            h = number[:2] + '.' + number[2:]
            j = round(float(h))
            g = str(j) + '0' * (len(number) - 2)
            return g
        elif 1 <= len(number) <= 4:
            h = number[:1] + '.' + number[1:]
            j = round(float(h))
            g = str(j) + '0' * (len(number) - 1)
            return g

    def __preparing_data(self, soup):
        """ Подготовка данных к их дальнейшему использованию. """
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

            if self.domain[self.count - 1] == site_name:
                for date in monthly_visits_top5:
                    self.monthly_visits.append(monthly_visits_top5[date])
                    print(site_name, date, self.__rounding(monthly_visits_top5[date]))

                print(site_name + '\t' + 'Total Traffic' + '\t' + str(self.__rounding(self.monthly_visits[-1])))

                for country in top_country:
                    country_name = const_countries[str(country['Country'])]
                    top5_traffic = self.__rounding(round(self.monthly_visits[-1] * country['Value']))
                    print(site_name, country_name, top5_traffic)
            else:
                print('https://www.similarweb.com/website/' + str(self.domain[self.count - 1]))

    def run(self):
        """ Главная функция. """
        self.__create_list_of_domains()
        while True:
            if self.count == len(self.domain):
                self.driver.quit()
                break
            self.count += 1
            self.driver.get(f'https://data.similarweb.com/api/v1/data?domain={self.domain[self.count - 1]}')
            source = self.driver.page_source
            soup = BeautifulSoup(source, 'html.parser')
            self.__preparing_data(soup=soup)

            print(soup)  # убрать после отладки


if __name__ == '__main__':
    similar = Similar(headless=False)  # Если False - браузер будет виден, если True - не будет
    similar.run()
