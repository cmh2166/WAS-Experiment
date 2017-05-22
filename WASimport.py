#!/usr/bin/env python

from __future__ import print_function

__version__ = '0.0.1' # also in setup.py

from argparse import ArgumentParser
import configparser
import datetime
import json
import pprint
import requests
from requests.auth import HTTPBasicAuth
import time
import yaml


class WASAPIFile:
    """Class to handle WASAPI file


def generateFileList(WASAPI_resp, files):
    """Create a Python list of file dictionaries from WASAPI."""
    if 'files' in WASAPI_resp:
        if files:
            files.extend(WASAPI_resp['files'])
        else:
            files = WASAPI_resp['files']
    else:
        print('Error: no Files in WASAPI response.')
        exit()
    return(files)


def getWebData(WASAPI_endpoint, auth, files=None, date_before=None,
               date_after=None, job_id=None, coll_id=None):
    if 'webdata' not in WASAPI_endpoint:
        WASAPI_URL = WASAPI_endpoint + 'webdata?format=json'
    else:
        WASAPI_URL = WASAPI_endpoint
    if date_before:
        WASAPI_URL += '&crawl-start-before=' + date_before
    if date_after:
        WASAPI_URL += '&crawl-start-after=' + date_after
    if job_id:
        WASAPI_URL += '&job=' + str(job_id)
    if coll_id:
        WASAPI_URL += '&collection=' + str(coll_id)

    print("Trying URL: " + WASAPI_URL)

    resp = requests.get(WASAPI_URL, auth=auth)

    if resp.status_code == requests.codes.ok:
        ait_data = resp.json()
        files = generateFileList(ait_data, files)
        if 'next' in ait_data:
            if ait_data['next']:
                getWebData(ait_data['next'], auth, files)
    else:
        print("Error with URL.")
        exit()
    print(len(files))
    return(files)


def authenticate(username, password):
    auth = HTTPBasicAuth(username, password)
    return(auth)


def main():
    parser = ArgumentParser(usage='%(prog)s [options]')
    parser.add_argument("-b", "--before", dest="date_before")
    parser.add_argument("-a", "--after", dest="date_after")
    parser.add_argument("-j", "--job", dest="job_id")
    parser.add_argument("-c", "--coll", dest="coll_id")
    args = parser.parse_args()

    cfg = yaml.load(open('shared_configs/aip-creds.yml', 'r'))
    username = cfg['development-ait']['username']
    password = cfg['development-ait']['password']
    WASAPI_endpoint = cfg['development-ait']['WASAPI-endpoint']

    ait_auth = authenticate(username, password)
    getWebData(WASAPI_endpoint, ait_auth, args.date_before, args.date_after, args.job_id, args.coll_id)


if __name__ == '__main__':
    main()
