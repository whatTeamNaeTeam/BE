from django.utils.deprecation import MiddlewareMixin


class AttachJWTFromHeaderToCookieMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.APIS = ["github/login", "github/finish"]
        self.REFRESH = "token/refresh"

    def process_response(self, request, response):
        path = request.path_info
        is_valid = any(api in path for api in self.APIS)
        is_refresh = True if self.REFRESH in path else False

        if is_valid or is_refresh:
            if request.META.get("HTTP_FROM", None) == "web":
                print(response.data)
                response.set_cookie("refresh", response["refresh"])
                response.set_cookie("access", response["access"])

                if is_valid:
                    response.data.pop("access")
                    response.data.pop("refresh")

                response.content = response.render().rendered_content

        return response


class AttachJWTFromCookieToHeaderMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.NOT_APIS = ["github/login", "github/finish"]
        self.REFRESH = "token/refresh"

    def process_request(self, request):
        path = request.path_info
        is_valid = any(api in path for api in self.NOT_APIS)
        is_refresh = True if self.REFRESH in path else False

        if not is_valid:
            if request.META.get("HTTP_FROM", None) == "web":
                request.META["access"] = request.COOKIES.get("access", None)
                request.META["refresh"] = request.COOKIES.get("refresh", None)

        if is_refresh:
            if request.META.get("HTTP_FROM", None) == "web":
                request.META["refresh"] = request.COOKIES.get("refresh", None)
