class ProfileSerializerHelper:
    def make_data(self, owner_id, profile, url, tech):
        return {
            "profile": profile.data,
            "urls": self.make_url_data(url) if url else None,
            "tech": self.make_tech_data(tech) if tech else None,
            "is_owner": True if owner_id == profile.data["id"] else False,
        }


profileSerializerHelper = ProfileSerializerHelper()
