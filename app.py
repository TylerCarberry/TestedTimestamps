import json

import feedparser
import opencensus
from flask import Flask
from flask import render_template
from flask import request
import main
import os

import utils
import youtube_api

app = Flask(__name__)


@app.route('/')
def home():
    with utils.get_tracer().span(name='home'):
        with utils.get_tracer().span(name='Parse RSS feed'):
            feed = feedparser.parse(main.RSS_FEED)

        your_list = []
        for i in range(0, min(100, len(feed.entries))):
            your_list.append({"name": feed.entries[i].title, "url": feed.entries[i].enclosures[0].href})

        return render_template("index.html", your_list=your_list)


@app.route('/run')
def run_youtube():
    with utils.get_tracer().span(name='run_youtube'):
        return youtube_api.youtube_main(force=request.args.get("force"))


@app.route('/fromurl', methods=['GET', 'POST'])
def fromurl():
    url = request.form.get('url')
    name = request.form.get('name')

    if os.path.exists("episode.mp3"):
        os.remove("episode.mp3")

    if url in main.get_cache():
        return "<pre>" + name + "\n\n" + main.get_cache().get(url) + "</pre>"

    output = main.generate_timestamps(url)
    res = ""
    for item in output:
        res += main.FILE_NAMES_TO_NAME[item[0]] + " " + main.format_seconds(item[1]) + "\n"
    return "<pre>" + name + "\n\n" + res + "</pre>"


def generate_cached_data():
    feed = feedparser.parse(main.RSS_FEED)

    your_list = []
    for i in range(0, min(100, len(feed.entries))):
        your_list.append({"name": feed.entries[i].title, "url": feed.entries[i].enclosures[0].href})

    cache = {}
    for i in range(0, 20):
        if os.path.exists("episode.mp3"):
            os.remove("episode.mp3")

        url = your_list[i]['url']
        output = main.generate_timestamps(url)
        res = ""
        for item in output:
            res += main.FILE_NAMES_TO_NAME[item[0]] + " " + main.format_seconds(item[1]) + "\n"
        cache[url] = res

    print(json.dumps(cache))


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
