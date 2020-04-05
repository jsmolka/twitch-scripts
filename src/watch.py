import api
import argparse
from download import download
from time import sleep
from user import User


def fetch_video_ids(user_id):
    try:
        json = api.json("helix/videos", params={"user_id": user_id})
    except Exception as e:
        print("Fetching video IDs failed")
        print(str(e))
        return set()

    ids = set()
    for video in json.get("data", []):
        ids.add(video["id"])

    return ids


def watch(name):
    try:
        user = User.get_by_login(name)
        print("Watching user", name)
    except Exception as e:
        print("Fetching user failed", name)
        print(str(e))
        return

    ids = fetch_video_ids(user.id)

    while True:
        sleep(1800)

        new = fetch_video_ids(user.id).difference(ids)

        for video_id in new:
            download(video_id)

        ids.update(new)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", dest="user", type=str, help="user name", required=True)

    watch(parser.parse_args().user)
