import requests

from decouple import config
from enum import Enum

from py1337x import py1337x


class Constants(Enum):
    """Contains constants for the module."""
    TORRENTS = py1337x(cache='py1337xCache', cacheTime=500)
    API_URL = "https://api.short.io/links"
    DOMAIN = config('DOMAIN')
    API_KEY = config('API_KEY')
    HEADERS = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": API_KEY}
    USEFUL_KEYS = ['name', 'seeders', 'size', 'torrentId']


def search(search_query: str) -> list:
    """Searches 1337x with specified query."""
    raw_results = Constants.TORRENTS.value.search(search_query).get('items')
    results = []
    for result in raw_results:
        result['name'] = result.get('name')[:30]
        result = {key: result.get(key) for key in Constants.USEFUL_KEYS.value}
        results.append(result)
        if len(results) == 10:
            break
    return results


def get_magnet(torrentId: int) -> str:
    """Gets the magnet link for the specified torrent id and shortens it."""
    raw_result = Constants.TORRENTS.value.info(
        torrentId=torrentId).get('magnetLink')
    result = short_url(raw_result)
    return result


def short_url(url: str) -> str:
    """Shortens the URL with short.io API."""
    payload = {
        "domain": Constants.DOMAIN.value,
        "originalURL": url}
    response = requests.post(Constants.API_URL.value,
                             json=payload, headers=Constants.HEADERS.value)
    return response.json()['shortURL']
