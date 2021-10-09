import api
import m3u8
from user import User


class VideoSegment:
    def __init__(self, segment, muted_segments):
        self.id = int(segment.uri.replace(".ts", "").replace("-unmuted", ""))
        self.uri_base = segment.base_uri
        self.uri_name = segment.uri

        if self.id in muted_segments:
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
        self.fetch_segments()

    def fetch_helix(self):
        json = api.json("helix/videos", params={"id": self.id})
        data = json["data"][0]

        self.user = User.get_by_id(data["user_id"])
        self.created_at = data["created_at"]
        self.title = data["title"]
        self.url = data["url"]

    def fetch_kraken(self):
        json = api.json("kraken/videos/{}".format(self.id))

        self.live = json["status"] == "recording"
        self.preview_url = json["animated_preview_url"]

        self.muted_segments = set()
        for segment in json.get("muted_segments", []):
            self.muted_segments.update(range(
                segment["offset"] // 10,
                segment["offset"] // 10 + segment["duration"] // 10
            ))

    def fetch_segments(self):
        # Have: https://vod-storyboards.twitch.tv/the-thing-we-need/storyboards/521793143-strip-0.jpg
        # Want: https://d1ymi26ma8va5x.cloudfront.net/the-thing-we-need/chunked/index-dvr.m3u8
        m3u8_list = "https://d1ymi26ma8va5x.cloudfront.net/{}/chunked/index-dvr.m3u8".format(self.preview_url.split("/")[-3])
        m3u8_load = m3u8.load(m3u8_list)

        self.segments = [VideoSegment(segment, self.muted_segments) for segment in m3u8_load.segments]

    def update(self):
        self.fetch_kraken()
        self.fetch_segments()
