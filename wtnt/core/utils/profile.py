class ProfileResponse:
    @staticmethod
    def make_data(user, url, tech, owner_id):
        return {"profile": user, "url": url, "tech": tech, "is_owner": user["id"] == owner_id}

    @staticmethod
    def make_url_data(url):
        url = url["url"]
        data = url.split(",")
        return [{"url": url} for url in data]

    @staticmethod
    def make_tech_data(tech):
        tech = tech["tech"]
        data = tech.split(",")
        return [{"name": name} for name in data]

    @staticmethod
    def make_activity_data(teams, user_id, owner_id):
        return {"team": teams, "is_owner": user_id == owner_id}
