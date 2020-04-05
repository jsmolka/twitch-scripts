import api
import argparse
import os
import sys
import time
from video import Video


def encode(src, dst):
    params = [
        "-hide_banner",
        "-loglevel panic",
        "-i \"{}\"".format(src),
        "-acodec copy",
        "-bsf:a aac_adtstoasc",
        "-vcodec copy"
    ]
    return os.system("ffmpeg {} \"{}\"".format(" ".join(params), dst))


def concat(pattern, dst):
    windows = sys.platform == "win32"
    command = "copy /b \"{}\" \"{}\" >nul" if windows else "cat {} > \"{}\""

    return os.system(command.format(pattern, dst))


def process(video, segments):
    print("Processing {} segments".format(len(segments)))

    filename = "{} {}".format(
        video.user.login,
        video.created_at.split("T")[0].replace("-", "")
    )

    pattern = os.path.join(video.id, "*.ts")
    file_ts = os.path.join(video.id, filename + ".ts")
    file_mp = os.path.join(video.id, filename + ".mp4")

    if concat(pattern, file_ts) != 0:
        print("Failed concatenating segments")
        return

    for segment in segments:
        os.remove(segment)

    if encode(file_ts, file_mp) != 0:
        print("Failed encoding video")
        return

    os.remove(file_ts)


def download(id):
    try:
        video = Video(id)
        print("Downloading video", id)
    except Exception as e:
        print("Failed fetching video")
        print(str(e))
        return

    segments = []
    finished = set()

    os.makedirs(id, exist_ok=True)

    while True:
        for segment in video.segments:
            if segment.id in finished:
                continue

            try:
                response = api.get(segment.uri, stream=True)
                filename = "{}/{}".format(video.id, segment.filename)
                with open(filename, "wb") as data:
                    for chunk in response.iter_content(chunk_size=128):
                        data.write(chunk)

                segments.append(filename)
                finished.add(segment.id)

            except Exception as e:
                print("Failed downloading segment", segment.id)
                print(str(e))

        if not video.live:
            break

        time.sleep(300)

        try:
            video.update()
        except Exception as e:
            print("Failed updating video")
            print(str(e))
            break

    process(video, segments)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", dest="video", type=str, help="video id", required=True)

    download(parser.parse_args().video)
