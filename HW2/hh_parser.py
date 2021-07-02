import time

import requests
import sys
import argparse
import json
from pprint import pprint
from bs4 import BeautifulSoup as bs


class HHParser:
    proxy = {
        'http': 'http://110.249.176.26:8060',
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Content-Type": "text/html; charset=utf-8"
    }

    url = "https://hh.ru/search/vacancy"

    params = {
        "area": 1,
        "st": "searchVacancy",
        "text": "",
        "items_on_page": "20",
        "page": "0"
    }

    what = ['div', {'class': 'vacancy-serp-item'}]
    soup = None

    def __init__(self, vacancy: str, items_on_page="20", page="0"):
        """
        :param vacancy: string
        :param items_on_page: string, but integer
        :param proxy: 'http://ip:port'
        :param with_proxy: bool
        """
        with_proxy = False
        self.params['text'] = vacancy or 'python developer'
        self.params['items_on_page'] = items_on_page
        self.params['page'] = page

        if with_proxy is False:
            resp = requests.get(url=self.url, params=self.params,
                                headers=self.headers)
            if resp.status_code == 200:
                self.soup = bs(resp.text, 'html.parser') \
                    .find_all(*self.what)
            else:
                raise ConnectionError

        else:
            resp = requests.get(url=self.url, params=self.params,
                                headers=self.headers, proxies=self.proxy)
            if resp.status_code == 200:
                self.soup = bs(resp.text, 'html.parser') \
                    .find_all(*self.what)
                print(len(self.soup))
            else:
                raise ConnectionError

    def next_vacancy(self):
        for i in self.soup:
            yield Vacancy(i)


class Vacancy:
    vac = None

    def __init__(self, vac: bs):
        """
        :param vac: beautiful soup object
        """
        self.vac = vac

    @staticmethod
    def parse_salary(salary: str):
        """
        :param salary: 'от XXX до XXX руб', 'от XXX руб', 'до XXX руб'
        :return: [нижний порог, верхний порог, валюта] as list of str
        """
        sals = salary.split()
        if sals[0] == 'от':
            return sals[1], '', sals[2]
        elif sals[0] == 'до':
            return '', sals[1], sals[2]
        else:
            return sals[0], sals[2], sals[3]

    def get_link(self):
        try:
            return self.vac.find('a').get('href')
        except KeyError:
            print(f"no href for vacancy")
            return None

    def get_vacancy(self):
        try:
            return self.vac.find('a').text
        except AttributeError:
            print("Vacancy has no name")
            return None

    def get_salary(self):
        try:
            return \
                self.parse_salary(self.vac.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                                  .text.replace('\u202f', ''))
        except AttributeError:
            print(f"No info about vacancy salary")
            return 0, 0, None


def prepare_page(opts: argparse.Namespace):
    vacancies = []
    hhp = HHParser(vacancy=opts.q,
                   items_on_page=str(opts.i),
                   page=str(opts.p))
    for res in hhp.next_vacancy():
        next_v = {
            "link": res.get_link(),
            "name": res.get_vacancy(),
            "worst_offer": res.get_salary()[0],
            "best_offer": res.get_salary()[1],
            "currency": res.get_salary()[2]
        }

        vacancies.append(next_v)
    return vacancies


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="hh_parser.py -q <query> -p <pages> "
                                                 "[-i <items on page>]")
    parser.add_argument("-q", type=str, required=True)
    parser.add_argument("-p", default=0, type=int)
    parser.add_argument("-i", default=10, type=int)

    args = parser.parse_args()
    to_dump = []
    for i in range(0, args.p + 1):
        args.p = i
        for vac in prepare_page(args):
            to_dump.append(vac)
        time.sleep(1)

    with open("data_file.json", "w") as write_file:
        json.dump(to_dump, write_file)

    with open("data_file.json", 'r') as f:
        data = len(json.load(f))

    print(data)
