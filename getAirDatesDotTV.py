import requests
import re
from pprint import pprint
from bs4 import BeautifulSoup as bs
import json
from datetime import datetime
# import sys



urls = {
    "query": "https://www.airdates.tv/s?q=__QUERY__",
    "show": "https://www.airdates.tv/s?q=info%3A__ID__"
}

with open('db.json', 'r') as fp:
    db = json.load(fp)

tags = db['MY']['SERIES']['TAGS']
session = requests.session()
data = {}
for show in tags:
    data[show] = {}
    url = urls["query"].replace("__QUERY__", show)
    # print(url)
    response = session.get(url)
    content = response.content.decode()
    match = re.search("<li data-series-id=\"(\d+)\">", content)
    showId = match.group(1)
    # print(showId)
    # pprint(response.content.decode())

    url = urls["show"].replace("__ID__", showId)
    # print(url)
    response = session.get(url)
    # content = response.content.decode()
    # pprint(content)
    soup = bs(response.content, "html.parser")
    divs = soup.find_all('div', class_='title')
    for div in divs:
        strDiv = str(div)
        match = re.search("<div class=\"title\"><div class=\"tiny-date\">(.*?)</div>(.*?)</div>", strDiv)
        title = match.group(2)
        dateElem = div.find('div', class_="tiny-date")
        date = dateElem.get_text()
        if date == "":
            continue
        if date not in data[show]:
            data[show][date] = []
        data[show][date].append(title)
        # sys.exit()

    # query = "q: info:2342"

# pprint(data)
# sys.exit()
db["DB"] = data

watchlist = {}
for show in data:
    tag = '1970-01-01'
    if show in tags:
        tag = tags[show]

    watchlist[show] = {}
    oTag = datetime.strptime(tag, "%Y-%m-%d")
    # print(oTag)
    for date in sorted(data[show].keys()):
        # print(date)
        oDate = datetime.strptime(date, "%Y-%m-%d")
        if oDate > oTag:
            for ep in data[show][date]:
                if date not in watchlist[show]:
                    watchlist[show][date] = []
                watchlist[show][date].append(ep)

db["MY"]["SERIES"]["WATCHLIST"] = watchlist
# pprint(db)
# sys.exit()

# sys.exit()
with open('db2.json', 'w') as fp:
    json.dump(db, fp, indent=4, sort_keys=True)


def html(s):
    r = "<br/>\n".join(s)
    print(r)

printer = []
for show in watchlist:
    tag = db["MY"]["SERIES"]["TAGS"][show]
    printer.append("<b>{} [{}]</b>".format(show, tag))
    print("{} [{}]".format(show, tag))
    for date in watchlist[show]:
        for ep in sorted(watchlist[show][date]):
            printer.append("-- {} [{}]".format(ep, date))
            print("-- {} [{}]".format(ep, date))


# html(printer)