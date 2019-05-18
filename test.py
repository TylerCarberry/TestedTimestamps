import requests
import main
import os


def test_episode_495():
    temp_files = ["episode.mp3", "db.pklz"]
    for f in temp_files:
        if os.path.isfile(f):
            os.remove(f)

    r = requests.get("https://media.blubrry.com/thisisonlyatest/d2rormqr1qwzpz.cloudfront.net/podcast/thisisonlyatest_20190411.mp3")

    with open(main.PODCAST_FILE_NAME, 'wb') as f:
        f.write(r.content)
        f.close()

    res = main.generate_timestamps()

    expected = ["Intro", "Top Story", "Pop Culture News", "Technology News", "Moment of Science", "Pinball", "VR Minute", "Things That Annoy Me", "Outro"]

    assert len(expected) == len(res)


test_episode_495()