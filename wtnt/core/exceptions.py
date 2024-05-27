from rest_framework.exceptions import APIException


class IsNotLeaderException(APIException):
    status_code = 403
    default_detail = "It's not leader of team"


class IsNotOwner(APIException):
    status_code = 403
    default_detail = "It's not an owner"


class CodeNotMatchError(APIException):
    status_code = 400
    default_detail = "Code Not Matched"


class RefreshTokenExpired(APIException):
    status_code = 401
    default_detail = "Expired Refresh Token"


class CeleryTaskException(APIException):
    status_code = 400
    default_detail = ""
