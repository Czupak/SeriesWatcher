from abc import ABC

import tornado.ioloop
import tornado.web

header = """<html>
<head><title>SeriesWatcher</title>
<style type='text/css'>
body {
    font-family:Verdana;
    font-size: 12px;
}
table {
    border:1px solid;
}
td {
    border:1px dotted;
    border-color:gray;
    font-family:Verdana;
    font-size: 12px;
    vertical-align: top;
    margin: 20 20;
    min-width: 190px;
}
div {
    margin: 5 15;
}
img {
    border:0px;
}
a {
    color:black;
    text-decoration:underline;
    font-weight:bold;
}
a:hover {
    color:gray;
    text-decoration:none;
    font-weight:bold;
}
textarea,input,select,button {
    color: gray;
    border:solid 1px #9B9A9A;
    font-family:Verdana,sans-serif;
    font-size: 9px;
    color:#3266A2;
    background:#D9E5F3;
}
.formularz {
    color: gray;
    border:solid 1px #9B9A9A;
    font-family:Verdana,sans-serif;
    font-size: 9px;
    color:#3266A2;
    background:#D9E5F3;
}
</style>
</head>
<body>
<script src="https://unpkg.com/react@17/umd/react.development.js" crossorigin></script>
<script src="https://unpkg.com/react-dom@17/umd/react-dom.development.js" crossorigin></script>
<h3>ಠ_ಠ</h3>
"""

footer = """
<div id="react_shit"></div>
<script type="module" src='react.js'></script>
</body>
</html>"""


class BaseHandler(tornado.web.RequestHandler, ABC):
    def initialize(self, cb):
        self.cb = cb

    def header(self):
        self.write(header)

    def footer(self):
        self.write(footer)


class ReactHandler(BaseHandler, ABC):
    def get(self):
        js = """
    fetch('api/shows.json'
    ,{
      headers : { 
        'Content-Type': 'application/json',
        'Accept': 'application/json'
       }
    }
    )
      .then(function(response){
        console.log(response)
        return response.json();
      })
      .then(function(myJson) {
        console.log(myJson);
      });
"""
        self.write(js)
        self.set_header("Content-Type", 'application/javascript; charset=utf-8')

class ApiHandler(BaseHandler, ABC):
    def get(self, api, parm1=None, parm2=None):
        print(api, parm1, parm2)
        if api == 'shows':
            self.write(self.cb.shows)
        elif api == 'show':
            self.write(self.cb.get_show(parm1))
        elif api == 'seen':
            self.write(self.cb.get_seen(parm1, parm2))


class MainHandler(BaseHandler, ABC):
    def get(self, show_hidden=False):
        if show_hidden:
            show_hidden = True
        self.header()
        self.write("<input type='text' name='query'/><button onclick=\"window.location.href='/search/' + document.getElementsByName('query')[0].value;\">Search</button>")
        self.write(" | <a href='/'>Main</a>")
        self.write(" | <a href='/showhidden/'>Show Hidden</a>")
        self.write(" | <a href='/refresh/'>Refresh</a>")
        self.write("<table>")  # <tr><td></td><td></td><td></td></tr>")
        shows = self.cb.get_shows(show_hidden=show_hidden)
        for show_name in shows:
            show_id = shows[show_name]
            self.write(f"<tr><td><a href='/show/{show_id}'>{show_name}</a></td>")
            episodes = self.cb.get_seen_summary(str(show_id))
            self.write(f"<td>")
            for epp in episodes:
                self.write(f"{epp}<br/>")
            self.write("</td>")
            self.write(f"<td><a href='/hideshow/{show_id}'>(h)</a></td>")

            self.write("</tr>")
        self.write("</table>")
        self.footer()

class HideShowHandler(BaseHandler, ABC):
    def get(self, show_id):
        self.cb.hide_show(show_id)
        self.redirect(f"/")

class SearchHandler(BaseHandler, ABC):
    def get(self, query):
        self.header()
        self.write("<a href='/'>Main</a><hr/>")
        print(query)
        res = self.cb.search_show(query)
        for entry in res:
            self.write(f"<a href='/showadd/{entry['id']}/{entry['name']}'>{entry['name']} - {entry['id']}</a> <a href='https://www.tvmaze.com/shows/{entry['id']}/{entry['name']}' target=_blank>TVMaze</a><br/>")
        self.footer()

class ShowAddHandler(BaseHandler, ABC):
    def get(self, show_id, show_name):
        self.cb.add_show(show_name, show_id)
        self.redirect(f"/show/{show_id}")


class ShowHandler(BaseHandler, ABC):
    def get(self, show_id):
        self.header()
        self.write("<a href='/'>Main</a><hr/>")
        show = self.cb.get_show(show_id)
        self.write(f"<b>{show['name']}</b><hr/>")
        self.write("<table><tr><td>")
        self.write("<table>")
        for key in [i for i in show if i not in ['meta', 'episodes', 'api']]:
            self.write(f"<tr><td>{key}</td><td>{show[key]}</td></tr>")
        cols = ['genres', 'premiered', 'runtime', 'status', 'language']
        for col in show['meta']:
            if col not in cols:
                cols.append(col)
        for key in cols:
            val = show['meta'][key]
            if type(val) == dict:
                val = "<br/>".join([f"{k}: {val[k]}" for k in val])
            if key not in ['_links', 'name', 'summary', 'image', 'updated', 'webChannel', 'officialSite', 'weight', 'id', 'url']:
                self.write(f"<tr><td>{key}</td><td>{val}</td></tr>")

        self.write("</table></td>")
        self.write(f"<td><img src='{show['meta']['image']['medium']}' /></td></tr></table>")
        self.write("<hr/>")
        self.write(f"<h3>Episodes</h3><br/>")
        self.write(f"<a href='/collection/{show_id}'>Rescan collection</a><br/>")
        self.write("<table><tr><th>KEY</th><th>Date</th><th>Name</th><th>Type</th><th>Collection</th><th></th></tr>")
        ordered = sorted(show['episodes'], key=lambda item: (item.get("date"), item.get('key')), reverse=True)
        for episode in ordered:
            episode_id = str(episode['id'])
            seen = self.cb.get_seen(show_id, episode_id)
            style = 'background: #F9D750'
            if episode['future']:
                style = "color: gray"
            elif seen:
                style = "background: #90CF86"
            if not episode['number']:
                episode['number'] = '--'
            collection = self.cb.get_collection_str(show_id, episode_id)
            self.write(
                f"<tr style='{style}'><td>{episode['key']}</td><td>{episode['date']}</td><td>{episode['name']}</td>")
            self.write(f"<td>{episode['type']}</td>")
            self.write(f"<td>{collection}</td>")
            self.write(f"<td><a href='/toggle/{show_id}/{episode_id}'>Toggle</a> <a href='/seen/{show_id}/{episode_id}'>Seen</a> <a href='/unseen/{show_id}/{episode_id}'>Unseen</a></td></tr>")
        self.footer()


class EpisodeToggleHandler(BaseHandler, ABC):
    def get(self, show_id, episode_id):
        self.cb.toggle_seen(show_id, episode_id)
        self.redirect(f"/show/{show_id}")


class EpisodeSeenHandler(BaseHandler, ABC):
    def get(self, show_id, episode_id):
        self.cb.mark_seen(show_id, episode_id, True)
        self.redirect(f"/show/{show_id}")


class EpisodeUnseenHandler(BaseHandler, ABC):
    def get(self, show_id, episode_id):
        self.cb.mark_seen(show_id, episode_id, False)
        self.redirect(f"/show/{show_id}")


class CollectionRescanHandler(BaseHandler, ABC):
    def get(self, show_id):
        self.cb.match_collection_show(show_id)
        self.redirect(f"/show/{show_id}")


class DeleteCollectionHandler(BaseHandler, ABC):
    def get(self, show_id, episode_id):
        file = self.cb.get_collection(show_id, episode_id)
        if file:
            file = file.split(': ')[0]
            self.cb.collection_api.delete(file)
        else:
            print(f'No collection {file} for {show_id}/{episode_id}')
        self.redirect(f"/show/{show_id}")


class AssignCollectionHandler(BaseHandler, ABC):
    def get(self, show_id, episode_id, collection_id=None):
        if not collection_id:
            self.header()
            self.write("<a href='/'>Main</a><hr/>")
            collection_id = -1
            for file in self.cb.collection_api.files:
                collection_id += 1
                self.write(f"<a href='/assign_collection/{show_id}/{episode_id}/{collection_id}'>{file}</a><br/>")
            # self.cb.match_collection_show(show_id)
            self.footer()
        else:
            self.cb.assign_collection(show_id, episode_id, collection_id)
            self.redirect(f"/show/{show_id}")


class RefreshHandler(BaseHandler, ABC):
    def get(self):
        self.cb.refresh_cache()
        self.redirect(f"/")


class WebServer:
    def __init__(self, callback, port=81):
        self.callback = callback
        ws_map = [
            (r"/", MainHandler, dict(cb=callback)),
            (r"/(showhidden)/", MainHandler, dict(cb=callback)),
            (r"/refresh/", RefreshHandler, dict(cb=callback)),
            (r"/react.js", ReactHandler, dict(cb=callback)),
            (r"/api/(shows)\.json", ApiHandler, dict(cb=callback)),
            (r"/api/(shows)", ApiHandler, dict(cb=callback)),
            (r"/api/(show)/([0-9]+)", ApiHandler, dict(cb=callback)),
            (r"/api/(seen)/([0-9]+)/([0-9]+)", ApiHandler, dict(cb=callback)),
            (r"/search/(.*)$", SearchHandler, dict(cb=callback)),
            (r"/showadd/([0-9]+)/(.*)", ShowAddHandler, dict(cb=callback)),
            (r"/hideshow/([0-9]+)", HideShowHandler, dict(cb=callback)),
            (r"/show/([0-9]+)", ShowHandler, dict(cb=callback)),
            (r"/toggle/([0-9]+)/([0-9]+)", EpisodeToggleHandler, dict(cb=callback)),
            (r"/seen/([0-9]+)/([0-9]+)", EpisodeSeenHandler, dict(cb=callback)),
            (r"/unseen/([0-9]+)/([0-9]+)", EpisodeUnseenHandler, dict(cb=callback)),
            (r"/collection/([0-9]+)", CollectionRescanHandler, dict(cb=callback)),
            (r"/delete_collection/([0-9]+)/([0-9]+)", DeleteCollectionHandler, dict(cb=callback)),
            (r"/assign_collection/([0-9]+)/([0-9]+)", AssignCollectionHandler, dict(cb=callback)),
            (r"/assign_collection/([0-9]+)/([0-9]+)/([0-9]+)", AssignCollectionHandler, dict(cb=callback))
        ]
        self.app = self.make_app(ws_map)
        self.app.listen(port)

    def make_app(self, ws_map):
        return tornado.web.Application(ws_map)

    def loop(self):
        tornado.ioloop.IOLoop.current().start()
