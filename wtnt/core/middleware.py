from django.utils.deprecation import MiddlewareMixin
from rest_framework import status


class AttachJWTFromHeaderToCookieMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.API = ["github/login", "callback/github"]
        self.REFRESH = "token/refresh"
        self.LOGOUT = "logout"

    def process_response(self, request, response):
        path = request.path_info
        is_valid = any(api in path for api in self.API)
        is_refresh = True if self.REFRESH in path else False
        is_logout = True if self.LOGOUT in path else False

        if (
            is_valid
            or is_refresh
            and (response.status_code == status.HTTP_200_OK or response.status_code == status.HTTP_201_CREATED)
        ):
            if request.META.get("HTTP_X_FROM", None) == "web":
                response.set_cookie(
                    "access",
                    response.headers.get("access", None),
                    httponly=True,
                    samesite="none",
                    secure=True,
                    domain="whatmeow.shop",
                )
                if is_valid:
                    del response.headers["access"]

                response.content = response.render().rendered_content

        elif is_logout and response.status_code == status.HTTP_204_NO_CONTENT:
            for cookie_name in request.COOKIES:
                response.set_cookie(
                    cookie_name,
                    value="",
                    httponly=True,
                    samesite="none",
                    secure=True,
                    max_age=0,
                    domain="whatmeow.shop",
                )

            if request.META.get("HTTP_X_FROM", None) == "web":
                del response.headers["access"]

            response.content = response.render().rendered_content

        return response


class AttachJWTFromCookieToHeaderMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.NOT_API = ["github/login", "callback/github"]

    def process_request(self, request):
        path = request.path_info
        is_valid = any(api in path for api in self.NOT_API)

        if not is_valid:
            if request.META.get("HTTP_X_FROM", None) == "web":
                if request.COOKIES.get("access"):
                    request.META["HTTP_AUTHORIZATION"] = f"Bearer {request.COOKIES.get('access', None)}"
