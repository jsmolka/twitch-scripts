import api
import argparse
import os
import sys
import time
from printl import *
from video import *


def _process(video, parts):
    name = "{} {}".format(
        video.user,
        video.created_at.split("T")[0].replace("-", "")
    )

    pattern = os.path.join(video.id, "*.ts")
    output_ts = os.path.join(video.id, name + ".ts")
    output_mp = os.path.join(video.id, name + ".mp4")

    def concatenate():
        if sys.platform == "win32":
            return os.system("copy /b \"{}\" \"{}\" >nul".format(pattern, output_ts))
        else:
            return os.system("cat {} > \"{}\"".format(pattern, output_ts))

    if concatenate() != 0:
        printl("Failed concatenating parts")
        return

    for part in parts:
        os.remove(part)

    if os.system("ffmpeg -hide_banner -loglevel panic -i \"{}\" -acodec copy -bsf:a aac_adtstoasc -vcodec copy \"{}\"".format(output_ts, output_mp)) != 0:
        printl("Failed converting video")
        return

    os.remove(output_ts)


def download_video(id):
    video = None
    try:
        video = Video(id)
        printl("Downloading video", id)
    except Exception as e:
        printl("Failed video request")
        printl(str(e))
        return

    os.makedirs(id, exist_ok=True)

    parts = []
    finished = set()
    was_live = video.is_live

    while True:
        for segment in video.segments:
            if segment.id in finished:
                continue

            if (segment.id + 1) % 100 == 0:
                printl("Downloading segment", segment.id + 1, "/", len(video.segments))

            try:
                response = api.get(segment.uri, stream=True)
                filename = "{}/{}".format(video.id, segment.file_name)
                with open(filename, "wb") as data:
                    for chunk in response.iter_content(chunk_size=128):
                        data.write(chunk)

                parts.append(filename)
                finished.add(segment.id)

            except Exception as e:
                printl("Failed downloading segment", segment.id)
                printl(str(e))

        if not video.is_live and not was_live:
            break

        if video.is_live:
            printl("Stream is live - waiting 60 seconds")
            time.sleep(60)
        else:
            was_live = False
            printl("Stream was live - waiting 300 seconds")
            time.sleep(300)

        try:
            video.update()
        except Exception as e:
            printl("Failed updating video")
            printl(str(e))
            break

    printl("Downloaded", len(parts), "/", len(video.segments), "segments")
    printl("Processing segments")
    _process(video, parts)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", help="video id", required=True)
    parser.add_argument("-l", help="log file")

    args = parser.parse_args()

    printl_init(args.l)

    download_video(args.v)
