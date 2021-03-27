from serieswatcher import SeriesWatcher
from pprint import pprint

if __name__ == '__main__':
    sw = SeriesWatcher()
    sw.webserver.loop()
