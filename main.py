from serieswatcher import SeriesWatcher
from pprint import pprint

if __name__ == '__main__':
    sw = SeriesWatcher(port=81, collection_path='')
    sw.webserver.loop()
