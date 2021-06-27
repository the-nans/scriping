import os
import json
import requests
from pprint import pprint
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth


def get_repo_list(user:'Anonymous', token:''):
    """
    Sample func to auth in GitHub and get some data
    :param user: usesrname
    :param token: auth token
    :return: list of that user's repository names
    """
    r = requests.get(f'https://api.github.com/users/{u}/repos', auth=HTTPBasicAuth(u, t))
    dict_r = []
    if r.status_code == 200:
        for rep in r.json():
            dict_r.append(dict(rep)['full_name'])
    else:
        dict_r.append(f'Response code: {r.status_code}')
    return dict_r

def dump_repo_list(repo_list):
    try:
        with open('hw1.json', 'w') as f:
            json.dump(repo_list, f, indent=2)
            return 0
    except BaseException as e:
        print(e)
        return e

if __name__ == '__main__':
    load_dotenv()

    u = os.environ.get('GIT-USER')
    t = os.environ.get('GIT-TOKEN')

    if dump_repo_list(get_repo_list(u, t)) == 0:
        print('Data dumped to file')
    else:
        print('Data dump failed')


