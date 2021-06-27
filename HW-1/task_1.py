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


if __name__ == '__main__':
    load_dotenv()

    u = os.environ.get('GIT-USER')
    t = os.environ.get('GIT-TOKEN')

    print(get_repo_list(u, t))



