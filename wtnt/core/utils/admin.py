class TeamResponse:
    @staticmethod
    def make_team_manage_detail_data(members, team):
        leader_id = team.leader.id

        for i, member in enumerate(members):
            if member["id"] == leader_id:
                leader_info = members.pop(i)
                break

        return {
            "title": team.title,
            "leader_info": leader_info,
            "members_info": members,
            "member_count": len(members) + 1,
            "team_id": team.id,
        }
