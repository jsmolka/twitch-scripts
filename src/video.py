import api
import m3u8


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
    def file_name(self):
        return "{}.ts".format(str(self.id).zfill(5))


class Video:
    def __init__(self, id):
        self.id = id
        self._init_helix()
        self._init_kraken()
        self._init_segments()

    def _init_helix(self):
        json = api.get_json("helix/videos", params={"id": self.id})
        data = json["data"][0]

        self.user = data.get("user_name")
        self.created_at = data.get("created_at")
        self.title = data.get("title")
        self.url = data.get("url")

    def _init_kraken(self):
        json = api.get_json("kraken/videos/{}".format(self.id))

        self._status = json.get("status")
        self._preview_url = json.get("animated_preview_url")
        self._muted_segs = set()

        for seg in json.get("muted_segments", []):
            self._muted_segs.update(range(
                seg["offset"] // 10,
                seg["offset"] // 10 + seg["duration"] // 10
            ))

    def _init_segments(self):
        # Have: https://vod-storyboards.twitch.tv/the-thing-we-need/storyboards/521793143-strip-0.jpg
        # Want: https://vod-metro.twitch.tv/the-thing-we-need/chunked/index-dvr.m3u8
        m3u8_list = "https://vod-metro.twitch.tv/{}/chunked/index-dvr.m3u8".format(self._preview_url.split("/")[-3])

        m3u8_object = m3u8.load(m3u8_list)

        self.segments = [VideoSegment(seg, self._muted_segs) for seg in m3u8_object.segments]

    def update(self):
        self._init_kraken()
        self._init_segments()

    @property
    def is_live(self):
        return self._status == "recording"
