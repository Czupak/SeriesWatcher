# import show
from serieswatcher.sources import Sources
from serieswatcher.collection import Collection
from serieswatcher.webserver import WebServer
import json
import os
import datetime

class SeriesWatcher:
    def __init__(self):
        print('SeriesWatcher: __init__')
        self.sources_api = Sources()
        self.sources_api.set_source('tvmaze')
        self.shows = {}
        self.hidden = []
        self.cache = {}
        self.state = {}
        self.collection_api = Collection('G:\\TV')
        self.collection = {}

        self.read_config()
        # self.refresh_cache()
        # self.verify_collection()
        self.webserver = WebServer(self)

    def verify_collection(self):
        self.collection_api.scan()
        for show_id in self.collection:
            show = self.cache[show_id]
            for episode_id in self.collection[show_id]:
                episode = show[episode_id]
                self.collection_api.discover_show(show['name'], episode['key'])
        return

    def match_collection_show(self, show_id):
        if show_id not in self.collection:
            self.collection[show_id] = {}
        show = self.cache[show_id]
        for episode in show['episodes']:
            episode_id = str(episode['id'])
            if not self.get_seen(show_id, episode_id):
                ep_prob = self.collection_api.discover_show(show['name'], episode['key'])
                if ep_prob[1] > 0.75:
                    self.collection[show_id][episode_id] = ep_prob[0]
                else:
                    if episode_id in self.collection[show_id]:
                        del self.collection[show_id][episode_id]
        self.save_config()

    def assign_collection(self, show_id, episode_id, collection_id):
        if show_id not in self.collection:
            self.collection[show_id] = {}
        collection_id = int(collection_id)
        self.collection[show_id][episode_id] = self.collection_api.shorten_path_to_file(self.collection_api.files[collection_id])
        self.save_config()

    def get_collection(self, show_id, episode_id):
        if show_id in self.collection and episode_id in self.collection[show_id]:
            return self.collection[show_id][episode_id]
        return False

    def get_collection_str(self, show_id, episode_id):
        action = ''
        style = ''
        coll = self.get_collection(show_id, episode_id)
        if coll:
            msg = coll
            file = msg.split(': ')[0]
            is_deleted = self.collection_api.is_deleted(file)
            # if is_deleted:
            # style = 'color: gray'
            if self.get_seen(show_id, episode_id):
                if is_deleted:
                    style = 'color: gray'
                else:
                    style = 'color: red'
                    action = f" <a href='/delete_collection/{show_id}/{episode_id}'>d</a>"
            elif is_deleted:
                    style = 'color: red'
        else:
            style = 'color: gray'
            msg = f"Nothing"
            if not self.get_seen(show_id, episode_id):
                msg += f" <a href='/assign_collection/{show_id}/{episode_id}'>a</a>"
        ret = f"<span style='{style}'>{msg}</span>{action}"
        return ret

    def read_config(self):
        if os.path.isfile('config.json'):
            with open('config.json', 'r') as fh:
                config = json.load(fh)

            def read_config_for_key(key):
                empty = {} if key != 'hidden' else []
                return config[key] if key in config else empty

            self.shows = read_config_for_key('shows')
            self.cache = read_config_for_key('cache')
            self.state = read_config_for_key('state')
            self.collection = read_config_for_key('collection')
            self.hidden = read_config_for_key('hidden')

    def save_config(self):
        config = {
            'shows': self.shows,
            'cache': self.cache,
            'state': self.state,
            'collection': self.collection,
            'hidden': self.hidden,
        }
        with open('config.json', 'w') as fh:
            json.dump(config, fh)

    def key_gen(self, season, number):
        if not number or number == '--':
            return f"S{season:02d}E--"
        return f"S{season:02d}E{number:02d}"

    def get_seen_summary(self, show_id):
        show = self.get_show(show_id)
        if show_id not in self.state:
            episodes = show['episodes']
        else:
            episodes = [i for i in show['episodes'] if str(i['id']) not in self.state[show_id]]
        episodes = sorted(episodes, key=lambda item: item.get("date"), reverse=False)
        res = []
        def format_episodes(episodes):
            ret = []
            for i in episodes:
                dt = datetime.date.fromisoformat(i['date'])
                style = 'background: #D9E33069'
                if dt > datetime.date.today():
                    style = "color: gray"
                ret.append(f"<span style='{style}'>[{i['date']}] {self.key_gen(i['season'], i['number'])} {i['name']}</span>")
            return ret

        if len(episodes) <= 5:
            res = format_episodes(episodes)
        else:
            res = format_episodes(episodes[0:2])
            res.append(f"...{len(episodes) - 5} more...")
            res += format_episodes(episodes[len(episodes)-2:len(episodes)])
        return res

    def get_seen(self, show_id, episode_id):
        show_id = str(show_id)
        episode_id = str(episode_id)
        # print("get_state: ", str(show_id), '+', str(episode_id))
        if show_id not in self.state:
            return False
        if episode_id not in self.state[show_id]:
            return False
        return self.state[show_id][episode_id]

    def set_seen(self, show_id, episode_id, seen=True):
        show_id = str(show_id)
        episode_id = str(episode_id)
        if seen:
            if show_id not in self.state:
                self.state[show_id] = {episode_id: True}
            elif episode_id not in self.state[show_id]:
                self.state[show_id][episode_id] = True
        else:
            if show_id in self.state and episode_id in self.state[show_id]:
                del(self.state[show_id][episode_id])

    def toggle_seen(self, show_id, episode_id):
        # print("toggle_state: ", str(show_id), '+', str(episode_id))
        self.set_seen(show_id, episode_id, not self.get_seen(show_id, episode_id))
        self.save_config()

    def mark_seen(self, show_id, episode_id, seen=True):
        show = self.get_show(show_id)
        ordered = sorted(show['episodes'], key=lambda item: (item.get("date"), item.get('key')), reverse=seen)
        mark_flag = False
        for episode in ordered:
            if str(episode['id']) == episode_id:
                mark_flag = True
            if mark_flag:
                self.set_seen(show_id, episode['id'], seen)
        self.save_config()

    def mark_unseen(self, show_id, episode_id):
        show = self.get_show(show_id)
        ordered = sorted(show['episodes'], key=lambda item: (item.get("date"), item.get('key')), reverse=False)
        mark_flag = False
        for episode in ordered:
            if str(episode['id']) == episode_id:
                mark_flag = True
            if mark_flag:
                self.set_seen(show_id, episode['id'], True)
        self.save_config()

    def add_show(self, name, id):
        print('add_show [', name, '+', str(id), ']')
        self.shows[name] = str(id)
        self.refresh_cache(name)
        self.save_config()

    def hide_show(self, show_id):
        if show_id in self.hidden:
            self.hidden.remove(show_id)
        else:
            self.hidden.append(show_id)
        self.save_config()

    def get_show(self, id, force_refresh=False):
        # print('get_show(' + str(id) + ')')
        if id not in self.cache or force_refresh:
            show = self.sources_api.get_show(id)
            for episode in show['episodes']:
                episode['key'] = self.key_gen(episode['season'], episode['number'])
                if episode['date'] == '':
                    episode['date'] = '2999-12-31'
            self.cache[id] = show
            self.save_config()

        res = self.cache[id]
        for episode in res['episodes']:
            dt = datetime.date.fromisoformat(episode['date'])
            if dt > datetime.date.today():
                episode['future'] = True
            else:
                episode['future'] = False

        return res

    def search_show(self, query):
        return self.sources_api.search(query)

    def get_shows(self, show_hidden=False):
        shows = {}
        for show_name in sorted(self.shows.keys()):
            if str(self.shows[show_name]) not in self.hidden or show_hidden:
                shows[show_name] = str(self.shows[show_name])
        return shows

    def refresh_cache(self, single_show=None):
        print('refresh_cache: ', single_show)
        if single_show:
            if single_show not in self.shows:
                print('Show not added: ' + single_show)
                return
            self.get_show(self.shows[single_show], force_refresh=True)
        else:
            for show in self.shows:
                print('refresh_cache2: ' + show)
                self.get_show(self.shows[show], force_refresh=True)
        self.collection_api.scan()
        self.save_config()
