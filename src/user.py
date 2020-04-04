import api


class User:
    def __init__(self, name):
        self.name = name
        self._init_helix()

    def _init_helix(self):
        json = api.get_json("helix/users", params={"login": self.name})

        self.id = json["data"][0]["id"]
