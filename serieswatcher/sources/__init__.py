# from serieswatcher.sources.imdb import IMDB
# from serieswatcher.sources.moviedatabase import MovieDatabase
from serieswatcher.sources.tvmaze import TVMaze


class Sources:
    def __init__(self):
        print('SeriesWatcher.Sources: __init__')
        self.list = {
            # 'moviedatabase': MovieDatabase(),
            # 'imdb': IMDB(),
            'tvmaze': TVMaze()
        }
        self.__api = None

    def set_source(self, source):
        if source in self.list:
            self.__api = self.list[source]
        else:
            print('No such source: ' + source)

    def get_show(self, id=None):
        data = self.__api.get_show(id)
        return data

    def search(self, query):
        return self.__api.search(query)

    # def get_by_id(self, id):
    #     return self.__api.get_by_id(id)
