import requests

proxies = {
    "http": "http://127.0.0.1:3000",
}


def search_musics_by_keyword_and_pagecode(kw, pagecode=1):
    payload = {
        'keywords': kw,
        'limit': 5,
        'offset': (pagecode - 1) * 5
    }
    response = requests.get('http://localhost/search', params=payload, proxies=proxies)

    return response.json()
