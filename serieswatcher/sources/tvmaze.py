"""TVMaze Class

"""
from serieswatcher.sources.basesource import BaseSource
import requests
import json


class TVMaze(BaseSource):
    def __init__(self):
        print('SeriesWatcher.Sources.TVMaze: __init__')
        super().__init__()
        self.name = ''
        self.api['url'] = "http://api.tvmaze.com"
        self.api['search_url'] = self.api['url'] + '/search/shows'
        self.api['show_url'] = self.api['url'] + '/shows/%ID%'
        self.api['episodes_url'] = self.api['url'] + '/shows/%ID%/episodes?specials=1'
        self.columns = ['year', 'tvrage_id', 'imdb_id', 'thetvdb_id', 'genres', 'status']
        for col in self.columns:
            self.meta[col] = ''

    def search(self, query):
        print('Find: ', query)
        querystring = {"q": query}
        response = requests.request("GET", self.api['search_url'], headers={}, params=querystring)
        result = []
        from pprint import  pprint
        # pprint(json.loads(response.text))
        for entry in json.loads(response.text):
            result.append({
                'name': entry['show']['name'],
                'id': entry['show']['id'],
                'year': entry['show']['premiered'] and entry['show']['premiered'][:4] or ''
            })
        return result

    def get_show(self, id=None):
        self.name = ''
        self.meta = {}
        self.episodes = []
        if id:
            self.get_meta(id)
            self.get_episodes(id)
        info = {
            'api': 'tvmaze',
            'name': self.name,
            'meta': self.meta,
            'episodes': self.episodes
        }
        return info

    def get_meta(self, id):
        print('Get Meta: ', str(id))
        url = self.api['show_url'].replace('%ID%', str(id))
        response = requests.request("GET", url, headers={}, params={})
        entry = json.loads(response.text)
        self.id = str(entry['id'])
        self.name = entry['name']
        self.meta['year'] = entry['premiered'][:4]
        for col in ['tvrage', 'imdb', 'thetvdb']:
            self.meta[col + '_id'] = entry['externals'][col]
        self.meta['genres'] = ', '.join(entry['genres'])
        for col in entry:
            if col not in ['externals', 'genres']:
                self.meta[col] = entry[col]


    def get_episodes(self, id):
        print('Get Episodes: ', str(id))
        url = self.api['episodes_url'].replace('%ID%', str(id))
        response = requests.request("GET", url, headers={}, params={})
        for episode in json.loads(response.text):
            self.episodes.append({
                'id': episode['id'],
                'name': episode['name'],
                'date': episode['airdate'],
                'season': episode['season'],
                'number': episode['number'],
                'type': episode['type'],
            })
