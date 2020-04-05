import api
import argparse
import time
from download import download
from user import User


def get_video_ids(user_id):
    try:
        json = api.json("helix/videos", params={"user_id": user_id})
    except Exception as e:
        print("Failed getting video ids")
        print(str(e))
        return set()

    ids = set()
    for video in json.get("data", []):
        ids.add(video.get("id"))

    return ids


def watch_user(name):
    user = None
    try:
        user = User(name)
        print("Watching user", name)
    except Exception as e:
        print("Failed user request", name)
        print(str(e))
        return

    ids = get_video_ids(user.id)

    while True:
        time.sleep(1800)

        new_ids = get_video_ids(user.id).difference(ids)

        for video_id in new_ids:
            download_video(video_id)

        ids.update(new_ids)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", help="user name", required=True)
    parser.add_argument("-l", help="log file")

    args = parser.parse_args()

    print_init(args.l)

    watch_user(args.u)
