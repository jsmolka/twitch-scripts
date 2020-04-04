import api
import argparse
import time
from download_video import *
from printl import *
from user import *


def _get_video_ids(user_id):
    try:
        json = api.get_json("helix/videos", params={"user_id": user_id})
    except Exception as e:
        printl("Failed getting video ids")
        printl(str(e))
        return set()

    video_ids = set()
    for video in json.get("data", []):
        video_ids.add(video.get("id"))

    return video_ids


def watch_user(name):
    user = None
    try:
        user = User(name)
        printl("Watching user", name)
    except Exception as e:
        printl("Failed user request", name)
        printl(str(e))
        return

    ids = _get_video_ids(user.id)

    while True:
        time.sleep(1800)
        printl("Updating video ids")

        new_ids = _get_video_ids(user.id).difference(ids)

        for video_id in new_ids:
            download_video(video_id)

        ids.update(new_ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="user name", required=True)
    parser.add_argument("-l", help="log file")

    args = parser.parse_args()

    printl_init(args.l)

    watch_user(args.u)
