#!/usr/bin/python3
# -*- coding: utf-8 -*-
import argparse
import hashlib
import json
import os
import sys

pwd = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(pwd, '../../../'))

import base64
import requests

from project_settings import project_path


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--host',
        default='127.0.0.1',
        # default='10.75.27.247',
        type=str,
    )
    parser.add_argument(
        '--port',
        default=9080,
        type=int,
    )
    args = parser.parse_args()

    return args


def main():
    args = get_args()

    url = 'http://{host}:{port}/HeartBeat'.format(
        host=args.host,
        port=args.port,
    )

    resp = requests.get(url)
    print(resp.text)
    # print(resp.json())
    return


if __name__ == '__main__':
    main()
