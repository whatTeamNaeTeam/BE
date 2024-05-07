from rest_framework.exceptions import APIException


class IsNotLeaderException(APIException):
    status_code = 403
    default_detail = "It's not leader of team"
