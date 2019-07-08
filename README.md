# Tested Timestamp Bot

Generates timestamps for the Tested Podcast [This is Only a Test](https://www.tested.com/podcast/this-is-only-a-test/) by listening for the transistion music.

[Example](https://www.youtube.com/watch?v=Szk0Lqe3qlM&lc=UgwEXngHAyQ6Nwr9eFh4AaABAg)

<img width="836" alt="Screen Shot 2019-07-07 at 8 22 39 PM" src="https://user-images.githubusercontent.com/6628497/60775843-ff778c80-a0f4-11e9-89bb-03cdcd5fbd7d.png">

## How it works

The hosts of the podcast play transition music before talking about different topics. This YouTube bot listens for those audio clips and generates episode timestamps when these cues are played.

* Every hour the bot checks the newest published podcast
* If there's a new episode it downloads the mp3 and breaks it up into pieces using ffmpeg
* Using [audfprint](https://github.com/dpwe/audfprint) it finds the position of the audio cues within the podcast
* Then it posts a comment on the video using the YouTube API

