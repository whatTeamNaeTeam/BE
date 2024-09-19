def attach_cookie(response, cookie_name, token):
    response.set_cookie(
        cookie_name,
        value=token,
        httponly=True,
        samesite="none",
        secure=True,
        domain=".whatmeow.shop",
    )

    return response


def delete_cookie(response, cookie_name):
    response.set_cookie(
        cookie_name,
        value="",
        httponly=True,
        samesite="none",
        secure=True,
        max_age=0,
        domain=".whatmeow.shop",
    )

    return response
