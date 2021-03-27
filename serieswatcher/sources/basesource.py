"""Source Class

"""


class BaseSource:
    def __init__(self):
        print('SeriesWatcher.Sources.BaseSource: __init__')
        self.id = ''
        self.name = ''
        self.api = {'url': ''}
        self.meta = {}
        self.columns = []
        self.episodes = []
        return

    def find(self, query):
        print('__Find: ', query)

    def get_meta(self, id):
        print('__Get Meta: ', str(id))

    def get_episodes(self, id):
        print('__Get Episodes: ', str(id))
