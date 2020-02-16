#!/usr/bin/env python
# -*-coding:utf-8-*-
import requests
import random
import time


def getUrlText(url, headers = None, params = None, timeout = 5):
    import requests
    if not headers:
        headers = {}
    if not params:
        params = {}
    base_headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.79 Safari/537.36',
    }
    base_headers.update(headers)

    base_params = {

    }
    base_params.update(params)

    try:
        html = requests.get(url, params=base_params, headers=base_headers, timeout = timeout)
        return html.text

    except BaseException:
        print('request error')
        return None



