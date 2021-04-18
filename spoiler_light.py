import os
import shutil
import easyocr
import time
import utils


VIDEO_FILE_NAME = "video"
FRAMES_FOLDER_NAME = "frames"
SECONDS_PER_FRAME = 15
VIDEO_RESOLUTION = 360


def get_start_and_end_spoiler_seconds(video_id):
    if video_id is None:
        return None, None
    download_youtube_video(video_id)
    extract_images()

    files = os.listdir(FRAMES_FOLDER_NAME)
    num_images = len(files) - 2  # Ignore . and .. files

    print(files)
    print("num_images", num_images)

    start = None
    end = None

    reader = easyocr.Reader(['en'])  # need to run only once to load model into memory

    # Frames are generated for every 15 seconds. Loop through 8 at a time (every 2 minutes)
    for i in range(1, num_images, 8):
        if does_image_contain_spoiler_light(reader, i):
            print("***")
            if start is None:
                start = i
            end = i


    print("Rough estimate", start, end)

    if start is None or end is None:
        return None, None

    # We have a rough estimate for the times
    BUFFER = 16
    for i in range(max(0, start-BUFFER), start):
        if does_image_contain_spoiler_light(reader, i):
            print("****")
            start = i
            break

    for i in range(min(end+BUFFER, num_images), end, -1):
        if does_image_contain_spoiler_light(reader, i):
            print("****")
            end = i
            break

    return start * SECONDS_PER_FRAME - SECONDS_PER_FRAME, end * SECONDS_PER_FRAME


def download_youtube_video(video_id):
    print("Downloading video video_id=", video_id)
    utils.delete_file_if_exists("video.mkv")
    video_url = "https://www.youtube.com/watch?v=" + video_id
    print("Downloading video video_url=", video_url)
    os.popen("youtube-dl -f 'bestvideo[height<={}]+bestaudio/best[height<={}]' -o '{}' '{}'".format(VIDEO_RESOLUTION, VIDEO_RESOLUTION, VIDEO_FILE_NAME, video_url)).read()


def extract_images():
    print("Extracting images")
    try:
        shutil.rmtree(FRAMES_FOLDER_NAME)
    except:
        # Folder doesn't exist
        pass
    utils.make_folder(FRAMES_FOLDER_NAME)
    os.popen("ffmpeg -i {}.mkv -vf fps=1/{} {}/%d.jpg".format(VIDEO_FILE_NAME, SECONDS_PER_FRAME, FRAMES_FOLDER_NAME)).read()


def does_image_contain_spoiler_light(reader, image_index):
    file_name = "{}/{}.jpg".format(FRAMES_FOLDER_NAME, str(image_index))
    print(file_name)
    res = reader.readtext(file_name)
    text = ""
    for text_block in res:
        if len(text_block) > 1:
            text += text_block[1] + " "
    return "spoil" in text.lower()

