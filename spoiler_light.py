import os
import shutil
import easyocr
import time
import utils


# 6 minutes 40 sec for 480p
# 4 minutes 30 for 360p


FRAMES_FOLDER_NAME = "frames"


def get_start_and_end_spoiler(video_id):
    if video_id is None:
        return None, None
    download_video(video_id)
    extract_images()

    files = os.listdir(FRAMES_FOLDER_NAME)
    num_images = len(files) - 2  # Ignore . and .. files

    start = None
    end = None

    reader = easyocr.Reader(['en'])  # need to run only once to load model into memory

    # Frames are generated for every 15 seconds. Loop through 8 at a time (every 2 minutes)
    for i in range(1, num_images, 8):
        if does_image_contain_spoiler_light(reader, i):
            if start is None:
                start = i
            end = i


    print("Rough estimate", start, end)

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

    return start, end


def download_video(video_id):
    utils.delete_file_if_exists("video.mkv")
    video_url = "https://www.youtube.com/watch?v=" + video_id
    os.popen("youtube-dl -f 'bestvideo[height<=360]+bestaudio/best[height<=360]' -o 'video' '{}'".format(video_url)).read()


def extract_images():
    try:
        shutil.rmtree(FRAMES_FOLDER_NAME)
    except:
        # Folder doesn't exist
        pass
    utils.make_folder(FRAMES_FOLDER_NAME)
    os.popen("ffmpeg -i video.mkv -vf fps=1/15 {}/%d.jpg".format(FRAMES_FOLDER_NAME)).read()


def does_image_contain_spoiler_light(reader, image_index):
    file_name = "{}/{}.jpg".format(FRAMES_FOLDER_NAME, str(image_index))
    print(file_name)
    res = reader.readtext(file_name)
    text = ""
    for text_block in res:
        if len(text_block) > 1:
            text += text_block[1] + " "
    return "spoil" in text.lower()

