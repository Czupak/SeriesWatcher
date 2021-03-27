"""Movie Database (IMDB Alternative) Class

"""
from serieswatcher.sources.basesource import BaseSource
import requests


class MovieDatabase(BaseSource):
    def __init__(self):
        print('SeriesWatcher.Sources.MovieDatabase: __init__')
        super().__init__()
        self.name = 'Movie Database (IMDB Alternative)'
        self.api['url'] = "https://movie-database-imdb-alternative.p.rapidapi.com/"
        self.columns = ['name']
        for col in self.columns:
            self.meta[col] = ''

    def search(self, query):
        print('Find: ', query)
        querystring = {"s": query, "page": "1", "r": "json"}
        headers = {
            'x-rapidapi-key': "test-key",
            'x-rapidapi-host': "movie-database-imdb-alternative.p.rapidapi.com"
        }
        response = requests.request("GET", self.api['url'], headers=headers, params=querystring)
        print(response.text)

    def get_by_id(self, id):
        self.get_meta()
        self.get_episodes()

    def get_meta(self, id):
        print('Get Meta: ', str(id))

    def get_episodes(self, id):
        print('Get Episodes: ', str(id))
