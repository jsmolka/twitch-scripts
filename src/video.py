import api
import m3u8
from user import User

class VideoSegment:
    def __init__(self, seg, muted_segs):
        self.id = int(seg.uri.replace(".ts", ""))
        self.uri_base = seg.base_uri
        self.uri_name = seg.uri

        if self.id in muted_segs:
            self.uri_name = self.uri_name.replace(".ts", "-muted.ts")

    @property
    def uri(self):
        return self.uri_base + self.uri_name

    @property
    def filename(self):
        return "{}.ts".format(str(self.id).zfill(5))


class Video:
    def __init__(self, id):
        self.id = id
        self.fetch_helix()
        self.fetch_kraken()
        self.init_segments()

    def fetch_helix(self):
        json = api.json("helix/videos", params={"id": self.id})
        data = json["data"][0]

        self.user = User.get_by_id(data["user_id"])
        self.created_at = data.get("created_at")
        self.title = data.get("title")
        self.url = data.get("url")

    def fetch_kraken(self):
        json = api.json("kraken/videos/{}".format(self.id))

        self.live = json.get("status") == "recording"
        self.preview_url = json.get("animated_preview_url")
        self.muted_segs = set()

        for seg in json.get("muted_segments", []):
            self.muted_segs.update(range(
                seg["offset"] // 10,
                seg["offset"] // 10 + seg["duration"] // 10
            ))

    def init_segments(self):
        # Have: https://vod-storyboards.twitch.tv/the-thing-we-need/storyboards/521793143-strip-0.jpg
        # Want: https://vod-metro.twitch.tv/the-thing-we-need/chunked/index-dvr.m3u8
        m3u8_list = "https://vod-metro.twitch.tv/{}/chunked/index-dvr.m3u8".format(self.preview_url.split("/")[-3])

        m3u8_object = m3u8.load(m3u8_list)

        self.segments = [VideoSegment(seg, self.muted_segs) for seg in m3u8_object.segments]

    def update(self):
        self.fetch_kraken()
        self.init_segments()
