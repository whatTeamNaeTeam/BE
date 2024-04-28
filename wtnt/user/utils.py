class ProfileSerializerHelper:
    def make_data(self, owner_id, profile, url, tech):
        return {
            "profile": profile.data,
            "urls": self.make_url_data(url.data["url"]) if url else None,
            "tech": self.make_tech_data(tech.data["tech"]) if tech else None,
            "is_owner": True if owner_id == profile.data["id"] else False,
        }

    def make_tech_data(self, tech):
        data = tech.split(",")
        return [{"name": name} for name in data]

    def make_url_data(self, url):
        data = url.split(",")
        return [{"url": url} for url in data]


profileSerializerHelper = ProfileSerializerHelper()
