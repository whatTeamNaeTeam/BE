from rest_framework.exceptions import APIException


class ClosedApplyError(APIException):
    status_code = 400
    default_detail = {"message": "마감된 지원입니다.", "code": "0500"}


class DuplicatedApplyError(APIException):
    status_code = 400
    default_detail = {"message": "중복된 지원입니다.", "code": "0501"}
