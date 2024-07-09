from rest_framework.exceptions import APIException


class UserNotFoundError(APIException):
    status_code = 404
    default_detail = {"message": "해당하는 유저가 존재하지 않습니다.", "code": "0000"}


class TeamNotFoundError(APIException):
    status_code = 404
    default_detail = {"message": "해당하는 팀이 존재하지 않습니다.", "code": "0001"}
