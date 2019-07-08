# https://github.com/dpwe/audfprint
from audfprint import audfprint

import os
import subprocess
import requests
import feedparser
import shutil

import training
from utils import text_between
from utils import format_seconds


RSS_FEED = "http://www.tested.com/podcast-xml/this-is-only-a-test/"

PODCAST_FILE_NAME = "episode.mp3"
NUM_CPU_CORES = 4
DEBUG_MODE = False

# To add a new segment, copy the transition music to the /transitions folder
# Add the filename and title to the dict below
FILE_NAMES_TO_NAME = {
    "intro.mp3": "Intro",
    "intro_dubstep.mp3": "Intro",
    "top_story.mp3": "Top Story",
    "pop_culture.mp3": "Pop Culture News",
    "technology_news.mp3": "Technology News",
    "moment_of_science.mp3": "Moment of Science",
    "vr_minute.mp3": "VR Minute",
    "annoy_me.mp3": "Things That Annoy Me",
    "pinball.mp3": "Pinball",
    "outro.mp3": "Outro"
}


startup_message = """
----------
| TESTED |
----------
Generate timestamps for This Is Only A Test
See README.txt for details
"""
print(startup_message)


def remove_temp_data():
    try:
        shutil.rmtree("parts")
    except:
        pass
    temp_files = ["result.txt"]
    for f in temp_files:
        if os.path.isfile(f):
            os.remove(f)


# Download the newest episode of the podcast
def download_newest_episode(url=None):
    if url is None:
        feed = feedparser.parse(RSS_FEED)
        download_url = feed.entries[0].enclosures[0].href
    else:
        download_url = url

    print("Downloading the episode from", download_url)
    r = requests.get(download_url)

    with open(PODCAST_FILE_NAME, 'wb') as f:
        f.write(r.content)
        f.close()


def split_episode_into_chunks():
    try:
        os.mkdir("parts")
    except FileExistsError:
        pass

    process = subprocess.Popen("ffmpeg -i episode.mp3 -f segment -segment_time 1800 -c copy parts/out%03d.mp3", shell=True, stdout=subprocess.PIPE)
    process.wait()

    parts = []
    for file in os.listdir("parts"):
        if "out" in file and ".mp3" in file:
            parts.append("parts/" + file)
    return sorted(parts)


def find_url_for_episode_number(num):
    feed = feedparser.parse(RSS_FEED)
    for episode in feed.entries:
        if "Episode " + num in episode.title:
            return episode.enclosures[0].href
    return None


def generate_timestamps(url=None):
    remove_temp_data()

    if not os.path.exists(training.DB_FILE):
        training.train()

    if not os.path.exists(PODCAST_FILE_NAME):
        download_newest_episode(url)

    print("\nGenerating data... This will take approximately 3 minutes")

    #audfprint.main(("audfprint match --dbase " + training.DB_FILE + " --match-win 10 --density 20  --min-count 5 --hashbits 30 --shifts 4 --ncores " + str(NUM_CPU_CORES) + " -x 9999 -T --opfile result.txt " + PODCAST_FILE_NAME).split())

    keyframes = {}
    parts = split_episode_into_chunks()

    part_num = 0
    for file in parts:
        audfprint.main(("audfprint match --dbase " + training.DB_FILE + " --match-win 3 --density 20  --min-count 5 --hashbits 10 --shifts 4 --ncores " + str(NUM_CPU_CORES) + " -x 9999 -T --opfile result.txt " + file).split())

        with open("result.txt", "r") as file:
            for line in file:
                if "Matched" in line:
                    file_name = text_between(line, "as transitions/", " at")
                    seconds_str = text_between(line, " at ", " s with")
                    seconds_str = seconds_str.replace("-", "").strip()
                    seconds = float(seconds_str) + part_num * 1800

                    num_found = text_between(line, "with ", "of ")
                    out_of = text_between(line, "of ", "common ")
                    accuracy = int(num_found) / int(out_of)

                    if keyframes.get(file_name) is None or keyframes.get(file_name)[2] < accuracy:
                        keyframes[file_name] = [file_name, seconds, accuracy]
        part_num += 1

    if not DEBUG_MODE:
        remove_temp_data()
    print()
    output = sorted(keyframes.values(), key=lambda x: x[1])
    for item in output:
        # Add a couple seconds to skip to the end of the music
        item[1] += 5
        print(FILE_NAMES_TO_NAME[item[0]], format_seconds(item[1]))

    return output

    # if len(output) <= 3:
    #     print("\nHmm... it only found a couple segments\nThe program will run again. Usually this fixes it.\n")
    #     training.train()
    #     return generate_timestamps()
    # else:
    #     return output


def get_cache():
    return {}
    #return {"https://media.blubrry.com/thisisonlyatest/d2rormqr1qwzpz.cloudfront.net/podcast/thisisonlyatest_20190516.mp3": "Technology News 22:41\nIntro 30:25\nTop Story 39:19\nPop Culture News 55:12\nMoment of Science 1:34:34\nVR Minute 1:46:53\nThings That Annoy Me 2:06:03\nOutro 2:14:34\n", "https://media.blubrry.com/thisisonlyatest/d2rormqr1qwzpz.cloudfront.net/podcast/thisisonlyatest_20190509.mp3": "Pop Culture News 3:47\nTechnology News 14:43\nIntro 30:48\nTop Story 47:20\nVR Minute 1:10:32\nIntro 1:33:26\nOutro 1:33:42\n"}


if __name__ == "__main__":
    generate_timestamps()
