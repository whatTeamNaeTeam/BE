class TeamResponse:
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
