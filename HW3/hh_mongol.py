import time
import requests
import argparse
from pprint import  pprint
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

MONGO_HOST = "localhost"
PORT = 27017
MONGO_DB = "head_hunt"
MONGO_COLLECTION = "vacancies"


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
            return "0", "0", None


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


def mongo_put(what: list):
    with MongoClient(MONGO_HOST, PORT) as client:
        db = client[MONGO_DB]
        vacancies = db[MONGO_COLLECTION]
        vacancies.insert_many(what)


def mongo_put_fresh(what: list):
    with MongoClient(MONGO_HOST, PORT) as client:
        db = client[MONGO_DB]
        vacancies = db[MONGO_COLLECTION]
        for that in what:
            doc_filter = that
            update = {
                "$set": that
            }
            vacancies.update_many(doc_filter, update, upsert=True)


def mongo_get(how_much: float):
    """
    :param float salary:
    :return: list of dictionaries
    """
    salary_filter = {
        "worst_offer": {"$gt": how_much}
    }
    with MongoClient(MONGO_HOST, PORT) as client:
        db = client[MONGO_DB]
        vacancies = db[MONGO_COLLECTION]
        good4you = vacancies.find(salary_filter)
    return good4you


def prepare_page(opts: argparse.Namespace):
    vacancies = []
    hhp = HHParser(vacancy=opts.q,
                   items_on_page=str(opts.i),
                   page=str(opts.p))
    for res in hhp.next_vacancy():
        w_o = float(res.get_salary()[0]) if len(res.get_salary()[0]) > 0 else 0.0
        b_o = float(res.get_salary()[1]) if len(res.get_salary()[1]) > 0 else 0.0
        next_v = {
            "link": res.get_link(),
            "name": res.get_vacancy(),
            "worst_offer": w_o,
            "best_offer": b_o,
            "currency": res.get_salary()[2]
        }

        vacancies.append(next_v)
    return vacancies


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="hh_mongol.py --put -q <query> -p <pages> "
                                                 "[-i <items on page>] \n "
                                                 "hh_mongol.py --get -l <lowest acceptable salary> ")
    subparsers = parser.add_subparsers(help="sub-command help")
    parser_put = subparsers.add_parser('put', help="For Put help enter put --help")

    parser_put.add_argument("-q", type=str, required=True, help="hh query")
    parser_put.add_argument("-p", default=1, type=int, help="result pages")
    parser_put.add_argument("-i", default=10, type=int, help="items on page")
    parser_put.add_argument("-f", action="store_true", help="put fresh vacancies only")

    parser_get = subparsers.add_parser('get', help="For Get help enter get --help")
    parser_get.add_argument("-l", required=True, type=float, help="lowest salary possible")
    args = parser.parse_args()

    try:
        to_dump = []
        for i in range(0, args.p):
            args.p = i
            for vac in prepare_page(args):
                to_dump.append(vac)
            time.sleep(1)

        if args.f is True:
            mongo_put_fresh(to_dump)
        else:
            mongo_put(to_dump)
    except AttributeError:
        pass

    try:
        for doc in mongo_get(args.l):
            pprint(doc)
    except AttributeError:
        pass
