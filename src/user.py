import api


class User:
    def __init__(self):
        pass

    def fetch(self, params):
        json = api.json("helix/users", params=params)
        data = json["data"][0]

        self.id = data["id"]
        self.name = data["display_name"]
        self.desc = data["description"]
        self.login = data["login"]

    @staticmethod
    def get_by_id(id):
        user = User()
        user.fetch({"id": id})

        return user

    @staticmethod
    def get_by_login(login):
        user = User()
        user.fetch({"login": login})

        return user
