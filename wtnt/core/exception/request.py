from rest_framework.exceptions import APIException


class InvalidRequestError(APIException):
    status_code = 400
    default_detail = {"message": "요청의 형식이 잘못되었습니다.", "code": "0010"}
