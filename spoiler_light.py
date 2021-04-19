import os
import shutil
import statistics

import easyocr
import time
import utils


VIDEO_FILE_NAME = "video"
FRAMES_FOLDER_NAME = "frames"
SECONDS_PER_FRAME = 10
VIDEO_RESOLUTION = 240


def get_start_and_end_spoiler_seconds(video_id):
    if video_id is None:
        return None, None
    download_youtube_video(video_id)
    extract_images()

    files = os.listdir(FRAMES_FOLDER_NAME)
    num_images = len(files) - 2  # Ignore . and .. files

    print(files)
    print("num_images", num_images)

    reader = easyocr.Reader(['en'])  # need to run only once to load model into memory

    images_that_contain_spoiler = []
    
    initial_precision = int(60 / SECONDS_PER_FRAME)
    for i in range(1, num_images, initial_precision):
        if does_image_contain_spoiler_light(reader, i):
            images_that_contain_spoiler.append(i)

    images_that_contain_spoiler = sorted(images_that_contain_spoiler)
    print(images_that_contain_spoiler)

    if len(images_that_contain_spoiler) == 0:
        return None, None

    start = images_that_contain_spoiler[0]
    end = images_that_contain_spoiler[-1]

    print(start, end)

    # We have a rough estimate for the times
    num_buffer_frames = int(initial_precision * 1.5)
    for i in range(max(0, start-num_buffer_frames), min(end+num_buffer_frames, num_images)):
        if i not in images_that_contain_spoiler and does_image_contain_spoiler_light(reader, i):
            images_that_contain_spoiler.append(i)

    images_that_contain_spoiler = sorted(images_that_contain_spoiler)
    start = images_that_contain_spoiler[0]
    end = images_that_contain_spoiler[-1]

    # Everything below this is used to find the longest duration that the spoiler light is shown for

    # Fill in any gaps of size 2 or smaller to fix any missing frames
    for i in range(start, end):
        if i not in images_that_contain_spoiler:
            # Gap of size 1
            if i+1 in images_that_contain_spoiler and i-1 in images_that_contain_spoiler:
                images_that_contain_spoiler.append(i)
            # Left side of gap of size 2
            elif i+2 in images_that_contain_spoiler and i-1 in images_that_contain_spoiler:
                images_that_contain_spoiler.append(i)
            # Right side of gap of size 2
            elif i+1 in images_that_contain_spoiler and i-2 in images_that_contain_spoiler:
                images_that_contain_spoiler.append(i)


    images_that_contain_spoiler = sorted(images_that_contain_spoiler)
    start, end = utils.longest_consecutive_sublist(images_that_contain_spoiler)

    print(start, end)
    return start * SECONDS_PER_FRAME - SECONDS_PER_FRAME - 5, end * SECONDS_PER_FRAME


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
    contains_spoiler_light = "spoil" in text.lower()
    if contains_spoiler_light:
        print("Found spoiler light at image_index", image_index)
    else:
        print("No spoiler light at image_index", image_index)
    return contains_spoiler_light

