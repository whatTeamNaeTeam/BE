def make_data(user, url, tech, user_id):
    return {"profile": user, "url": url, "tech": tech, "is_owner": user["id"] == user_id}


def make_url_data(url):
    data = url.split(",")
    return [{"url": url} for url in data]
