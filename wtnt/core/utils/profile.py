class ProfileResponse:
    @staticmethod
    def make_cached_data(user, url, tech):
        return {"profile": user, "url": url, "tech": tech}

    @staticmethod
    def make_data(data, owner_id):
        data["is_owner"] = data["profile"]["id"] == owner_id
        return data

    @staticmethod
    def make_url_data(url):
        try:
            data = url.split(",")
            return [{"url": url} for url in data]
        except Exception:
            return []

    @staticmethod
    def make_tech_data(tech):
        try:
            data = tech.split(",")
            return [{"name": name} for name in data]
        except Exception:
            return []

    @staticmethod
    def make_activity_data(teams, user_id, owner_id):
        return {"team": teams, "is_owner": user_id == owner_id}

    @staticmethod
    def make_team_manage_detail_data(members, team, _dict):
        leader_id = team.leader.id

        for i, member in enumerate(members):
            if member["id"] == leader_id:
                leader_key = i
                leader_info = member
                leader_info["category"] = _dict[leader_info["id"]]
                continue
            member["category"] = _dict[member["id"]]

        del members[leader_key]

        return {
            "title": team.title,
            "leader_info": leader_info,
            "members_info": members,
            "member_count": len(members) + 1,
            "team_id": team.id,
        }
