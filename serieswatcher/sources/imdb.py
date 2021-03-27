"""IMDB Class

"""
from basesource import BaseSource


class IMDB(BaseSource):
    def __init__(self):
        print('SeriesWatcher.Sources.IMDB: __init__')
        super().__init__()
        self.name = 'IMDB'
        self.columns = ['name']
        for col in self.columns:
            self.meta[col] = ''

    def search(self, query):
        print('Find: ', query)

    def get(self, id):
        self.get_meta()
        self.get_episodes()

    def get_meta(self, id):
        print('Get Meta: ', str(id))

    def get_episodes(self, id):
        print('Get Episodes: ', str(id))
