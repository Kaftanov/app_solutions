import requests
import re
import pandas as pd
import time

from bs4 import BeautifulSoup
from random import choice, uniform
from fake_useragent import UserAgent


class AvitoParser(object):
    """
        get_url
        get_last_page
        get_description_by_href
        get_titles
        append_df
        turning_pages
    """
    def __init__(self, base_url):
        self.base_url = base_url
        self.df = pd.DataFrame(columns=('title', 'href', 'descr'))
        self.proxy_list = []
        self.useragent_list = []
        self.user_agent = UserAgent()
        self.sessions = requests.Session()
        with open('proxy.txt') as file:
            for i in file:
                self.proxy_list.append('http://' + i.strip('\n'))

    def get_html(self, url):
        print('Checking: ' + url)
        time.sleep(uniform(2,3))
        proxy = {'http': choice(self.proxy_list)}
        user_agent = {'User-Agent': self.user_agent.random}
        return self.sessions.get(url, headers=user_agent, proxies=proxy).text

    def get_last_page(self, url):
        soup = BeautifulSoup(self.get_html(url), 'lxml')
        pages = soup.find('div', class_='pagination-pages').find_all('a', class_='pagination-page')
        pattern = re.compile('\?p=(\w+)\"')
        return int(pattern.search(str(pages[-1])).group(1))

    def get_description_by_href(self, href):
        base_url = 'https://www.avito.ru'
        url = base_url + href
        soup = BeautifulSoup(self.get_html(url), 'lxml')
        description = soup.find('div', class_='item-description-text')
        try:
            text = description.get_text()
        except AttributeError:
            text = str(description)
        return text
    
    def get_titles(self, base_url):
        soup = BeautifulSoup(self.get_html(base_url), 'lxml')
        ads = soup.find('div', class_='catalog-list clearfix').find_all('div', class_='item_table')
        temp_df = pd.DataFrame(columns=('title', 'href', 'descr'))
        for i,ad in enumerate(ads):
            title = ad.find('div', class_='description').find('h3', 'item-description-title')
            pattern_href = re.compile('href=\"(.+)\"\s')
            pattern_title = re.compile('title=[\',\"](.+)[\',\"]')
            href = pattern_href.search(str(title)).group(1)
            title_description = pattern_title.search(str(title)).group(1)
            temp_df.loc[i] = (title_description, href, self.get_description_by_href(href))

        self.df = self.df.append(temp_df, ignore_index=True)
        self.df.to_csv('log_dataset.csv')

    def turning_pages(self):
        url = self.base_url + '?p=%i'
        for i in range(1, self.get_last_page(self.base_url) + 1):
            self.get_titles(url % i)
        self.df.to_csv('dataset.csv')

url = 'https://www.avito.ru/moskva/kollektsionirovanie/monety'
kernel = AvitoParser(url)
kernel.turning_pages()
