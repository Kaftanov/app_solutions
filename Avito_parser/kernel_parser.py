import requests
import pandas as pd
import logging

from bs4 import BeautifulSoup
from random import choice, uniform
from re import compile
from time import sleep
from sys import exit


class AvitoParser(object):
    """
        get_url
        get_last_page
        get_description_by_href
        get_titles
        append_df
        turning_pages
    """
    # Standart imports
    default_proxy = ['http://160.16.94.228:80',
                     'http://114.179.245.22:80']
    default_UserAgent = 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36\
                         (KHTML, like Gecko) Chrome/27.0.1500.55 Safari/537.36'
    avito_url = 'https://www.avito.ru'

    def __init__(self, **kwargs):
        """
        Create base functionality for 'get_html' function
            parms:
            find params: list or tuple wich contain str objects.
            proxy: str object or list with proxy
                Default template file:
                    http://160.16.94.228:80
                    http://114.179.245.22:80
            path to UserAgent for parser: str object
                Default UserAgent:
                    if fake_useragent isn't installed use:

                    else:
                        use fake_useragent
        """
        frmt = '%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s'
        logging.basicConfig(format=frmt, level=logging.DEBUG,
                            filename='AvitoParserLog.log')
        # Base url
        try:
            self.base_url = kwargs['base_url']
        except KeyError as key_error:
            self.logging.critical("Can't start without param " + str(key_error))
            print("Can't start without param " + str(key_error))
            exit(-1)
        # proxy list
        try:
            self.find_params = kwargs['find_params']
        except KeyError:
            self.find_params = ('title', 'href')

        try:
            if type(kwargs['proxy']) is list:
                # list with proxies
                if kwargs['proxy'] is True:
                    self.proxy_list = kwargs['proxy']
            elif type(kwargs['proxy']) is str:
                # path to proxy
                if kwargs['proxy'] is True:
                    try:
                        with open('proxy.txt') as file:
                            for i in file:
                                self.proxy_list.append(i.strip('\n'))
                    except FileNotFoundError as file_error:
                        print(str(file_error))
                        self.proxy_list = self.default_proxy
        except KeyError:
            # These proxies work at 05.06.2017
            self.proxy_list = self.default_proxy

        # UserAgent
        try:
            from fake_useragent import UserAgent
            self.user_agent = UserAgent()
            self.isImport = True
        except ImportError as error:
            self.logging.warning("You haven't \"fake_useragent\" library" + str(error))
            print("You haven't \"fake_useragent\" library" + str(error))
        else:
            self.isImport = False
            self.user_agent = self.default_UserAgent

        try:
            self.time_delay = kwargs['time_delay']
        except KeyError as key_error:
            self.time_delay = (1, 2)

        self.df = pd.DataFrame(columns=self.find_params)
        # setup Session
        self.sessions = requests.Session()
        logging.info('\"__init__\" done')
        print('\"__init__\" done')

    def strip_quotes(self, url=None):
        """stripping quote from endline"""
        if url is None:
            self.logging.critical('"url" is None in "strip_quotes"')
            print('"url" is None in "strip_quotes"')
            exit(-1)
        pattern = compile(r'(.+)\"')
        striped_url = pattern.search(url).group(1)
        return url if striped_url is None else striped_url.strip(' ')

    def check_url(self, url=None):
        if url is None:
            self.logging.critical("\"url\" is None in \"check_url\"")
            print("\"url\" is None in \"check_url\"")
            exit(-1)
        html = self.get_html(url)
        if html is False:
            self.logging.critical("Can't access to url in \"get_html\"")
            print("Can't access to url in \"get_html\"")
            exit(-1)
        return html

    def is401(self, html=None):
        if html is None:
            return False
        soup = BeautifulSoup(html, 'lxml')
        try:
            pages = soup.find('div', class_='b-404').find('h1', '').get_text()
            if 'Ой! Такой страницы на нашем сайте нет' in pages:
                self.logging.warning('Error 401. Page not found')
                print('Error 401. Page not found')
                return True
        except AttributeError as error:
            return False

    def get_html(self, url=None):
        """
        Basic function for get page's html
            params:
                url: str object
        """
        if url is None:
            return False
        logging.info('Checking: ' + url)
        print('Checking: ' + url)
        # imitation user activity
        sleep(uniform(self.time_delay[0], self.time_delay[1]))
        proxy = {'http': choice(self.proxy_list)}
        if self.isImport is True:
            user_agent = {'User-Agent': self.user_agent.random}
        else:
            user_agent = {'User-Agent': self.user_agent}

        html = self.sessions.get(url, headers=user_agent, proxies=proxy).text
        # so stupid algorithm
        if self.is401(html):
            url = self.strip_quotes(url)
        else:
            return html
        html = self.sessions.get(url, headers=user_agent, proxies=proxy).text
        if self.is401(html):
            return False
        else:
            return html

    def get_last_page(self):
        """get last page in page list"""
        html = self.check_url(self.base_url)
        soup = BeautifulSoup(html, 'lxml')
        pages = soup.find('div', class_='pagination-pages')
        pages = pages.find_all('a', class_='pagination-page')
        pattern = compile('\?p=(\w+)\"')
        print(pages)
        # integer number palace on last position in list pages
        return int(pattern.search(str(pages[-1])).group(1))

    def get_description_by_href(self, href=None):
        if href is None:
            return 'Failed <href>'
        url = self.avito_url + href
        html = self.check_url(url)
        soup = BeautifulSoup(html, 'lxml')
        description = soup.find('div', class_='item-description-text')
        if description is None:
            return 'Failed'
        else:
            return description.get_text()

    def create_data(self, url=None):
        if url is None:
            logging.critical('Failed "url" in "create_data"')
            print('Failed "url" in "create_data"')
            exit(-1)
        html = self.check_url(url)
        soup = BeautifulSoup(html, 'lxml')
        ads = soup.find('div', class_='catalog-list clearfix')
        ads = ads.find_all('div', class_='item_table')
        # create log DataFrame for saving intermediate result
        temporary_df = pd.DataFrame(columns=self.find_params)
        try:
            for i, ad in enumerate(ads):
                if 'title' in self.find_params:
                    full_title = ad.find('div', class_='description')
                    full_title = full_title.find('h3', 'item-description-title')
                    pattern_title = compile('title=[\',\"](.+)[\',\"]')
                    title = pattern_title.search(str(full_title)).group(1)
                    if 'href' in self.find_params:
                        pattern_href = compile('href=\"(.+)\"\s')
                        href = pattern_href.search(str(full_title)).group(1)

                if 'sub_title' in self.find_params:
                    sub_title = ad.find('div', class_='about')
                    sub_title = sub_title.get_text().strip('\n').strip(' ')

                if 'description' in self.find_params:
                    description = self.get_description_by_href(href)

                for column in self.find_params:
                    if eval(column) is not None:
                        temporary_df.loc[i, column] = eval(column)
                    else:
                        continue

                self.df = self.df.append(temporary_df, ignore_index=True)
                self.df.to_csv('log_dataset.csv')
        except Exception as error:
            self.logging.critical('in \"create_data\"' + str(error))
            print('in \"create_data\"' + str(error))

    def turning_pages(self, log_level=None):
        url = self.base_url + '?p=%i'
        for i in range(1, self.get_last_page(self.base_url) + 1):
            self.get_titles(url % i)
        self.df.to_csv('dataset.csv')
