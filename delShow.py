import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--show', required=True, help="shows output")

args = parser.parse_args()

show = args.show
# date = args.date

with open('db.json', 'r') as fp:
    db = json.load(fp)

# print(show, date)
# print(db['MY']['SERIES']['TAGS'][show])
db['MY']['SERIES']['TAGS'].pop(show)
# print(db['MY']['SERIES']['TAGS'][show])

with open('db.json', 'w') as fp:
    json.dump(db, fp, indent=4, sort_keys=True)
