from django.utils.deprecation import MiddlewareMixin
from rest_framework import status

from .utils.cookie import delete_cookie, attach_cookie


class CustomLoginMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.API = ["github/login", "callback/github"]

    def process_response(self, request, response):
        path = request.path_info
        is_login = any(api in path for api in self.API)
        is_web = True if request.META.get("HTTP_X_FROM") else False

        if is_login and response.status_code in [status.HTTP_200_OK, status.HTTP_201_CREATED]:
            is_registered = response.data.get("registered", None)
            if is_web:
                cookie_name = "access" if is_registered else "temp"
                token = response.headers["access"]
                del response.headers["access"]
                response = attach_cookie(response, cookie_name, token)
            else:
                if not is_registered:
                    response.headers["temp"] = response.headers["access"]
                    del response.headers["access"]

            response.content = response.render().rendered_content

        return response


class CustomRegisterMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.API = "github/finish"

    def process_reponse(self, request, response):
        path = request.path_info
        is_register = True if self.API in path else False
        is_web = True if request.META.get("HTTP_X_FROM") == "web" else False

        if is_register:
            if is_web:
                token = request.COOKIES.get("temp")
                response = delete_cookie(response, "temp")
                response = attach_cookie(response, "access", token)
            else:
                response.headers["access"] = request.headers["temp"]

            response.content = response.render().rendered_content

        return response


class CustomRefreshMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.API = "token/refresh"

    def process_response(self, request, response):
        path = request.path_info
        is_refresh = True if self.API in path else False
        is_web = True if request.META.get("HTTP_X_FROM") == "web" else False

        if is_refresh:
            if response.status_code == status.HTTP_200_OK:
                if is_web:
                    token = response.headers.get("access", None)
                    response = attach_cookie(response, "access", token)
            elif response.status_code in [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED]:
                for cookie_name in request.COOKIES:
                    response = delete_cookie(response, cookie_name)
                if not is_web:
                    response.headers["access"] = ""

            response.content = response.render().rendered_content

        return response


class CustomLogoutMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.API = "logout"

    def process_response(self, request, response):
        path = request.path_info
        is_logout = True if self.API in path else False
        is_web = True if request.META.get("HTTP_X_FROM") == "web" else False

        if is_logout:
            if is_logout and response.status_code == status.HTTP_204_NO_CONTENT:
                for cookie_name in request.COOKIES:
                    response = delete_cookie(response, cookie_name)

                if is_web:
                    del response.headers["access"]

            response.content = response.render().rendered_content

        return response


class AttachJWTFromCookieToHeaderMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.NOT_API = ["github/login", "callback/github"]
        self.REGISTER = "github/finish"

    def process_request(self, request):
        path = request.path_info
        is_valid = any(api in path for api in self.NOT_API)
        is_register = True if self.REGISTER in path else False

        if not is_valid:
            if request.META.get("HTTP_X_FROM", None) == "web":
                if request.COOKIES.get("access"):
                    request.META["HTTP_AUTHORIZATION"] = f"Bearer {request.COOKIES.get('access', None)}"
                if is_register:
                    if request.COOKIES.get("temp"):
                        request.META["HTTP_AUTHORIZATION"] = f"Bearer {request.COOKIES.get('temp', None)}"
