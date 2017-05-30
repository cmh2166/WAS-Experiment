#!/usr/bin/env python

from __future__ import print_function

__version__ = '0.0.1' # also in setup.py

from argparse import ArgumentParser
import configparser
import datetime
import json
import pprint
import requests
import timeit
import yaml
from clint.textui import progress
import hashlib


class WASAPIFile:
    """Class to handle WASAPI files & metadata taken from REST API response."""
    def __init__(self, WAS_file):
        self.locations = WAS_file['locations']
        self.size = WAS_file['size']
        self.crawl = WAS_file['crawl']
        self.sha1 = WAS_file['checksums']['sha1']
        self.md5 = WAS_file['checksums']['md5']
        self.crawl_start = WAS_file['crawl-start']
        self.filetype = WAS_file['filetype']
        self.filename = WAS_file['filename']

    def grabFiles(self, client):
        for location in self.locations:
            print('Downloading file at ' + location)
            wasfile = client.get(location, stream=True)
            # To add: checksum validation, add output dir as config
            with open('sample_data/' + self.filename, 'wb') as fh:
                total_length = int(wasfile.headers.get('content-length'))
                for chunk in progress.bar(wasfile.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                    if chunk:
                        fh.write(chunk)
                        fh.flush()


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


def getWebData(WASAPI_endpoint, client, files=None, date_before=None,
               date_after=None, job_id=None, coll_id=None):
    if 'webdata' not in WASAPI_endpoint:
        WASAPI_URL = WASAPI_endpoint + 'webdata?format=json'
    else:
        WASAPI_URL = WASAPI_endpoint
    WASAPI_URL = 'https://partner.archive-it.org/wasapi/v1/webdata?format=json&collection=5425&page=5'
    if date_before:
        WASAPI_URL += '&crawl-start-before=' + date_before
    if date_after:
        WASAPI_URL += '&crawl-start-after=' + date_after
    if job_id:
        WASAPI_URL += '&job=' + str(job_id)
    if coll_id:
        WASAPI_URL += '&collection=' + str(coll_id)

    print("Trying URL: " + WASAPI_URL)

    resp = client.get(WASAPI_URL)

    if resp.status_code == requests.codes.ok:
        ait_data = resp.json()
        files = generateFileList(ait_data, files)
        if 'next' in ait_data:
            if ait_data['next']:
                getWebData(ait_data['next'], client, files)
    else:
        print(resp.status_code)
        print(resp.raw())
        print("Error with URL.")
        exit()
    return(files)


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
    WASAPI_login = cfg['development-ait']['WASAPI-login']

    # Authenticate / Create session & CSRF token
    client = requests.session()
    client.get(WASAPI_login)
    csrftoken = client.cookies['csrftoken']
    login_data = dict(username=username, password=password, csrfmiddlewaretoken=csrftoken, next="/")
    r = client.post(WASAPI_login, data=login_data, headers=dict(Referer=WASAPI_login))

    # Get list of file dictionaries from webdata API endpoint
    filelist = getWebData(WASAPI_endpoint, client, None, args.date_before,
                          args.date_after, args.job_id, args.coll_id)
    for WAS_file in filelist:
        WAS_file = WASAPIFile(WAS_file)
        WAS_file.grabFiles(client)



if __name__ == '__main__':
    main()
