from rest_framework.exceptions import APIException


class UserNameNotValidError(APIException):
    status_code = 400
    default_detail = {"message": "이름에 공백, 특수문자 또는 숫자가 포함되어 있습니다.", "code": "0100"}


class UserNameTooLongError(APIException):
    status_code = 400
    default_detail = {"message": "이름이 너무 짧거나 깁니다.", "code": "0101"}


class StudentNumNotValidError(APIException):
    status_code = 400
    default_detail = {"message": "학번에 공백,특수문자 또는 문자가 포함되어 있습니다.", "code": "0110"}


class StudentNumTooLongError(APIException):
    status_code = 400
    default_detail = {"message": "학번이 너무 짧거나 깁니다.", "code": "0111"}


class StudentNumDuplicatedError(APIException):
    status_code = 400
    default_detail = {"message": "중복된 학번입니다.", "code": "0112"}


class PositionNotValidError(APIException):
    status_code = 400
    default_detail = {"message": "포지션 기입이 올바르지 않습니다.", "code": "0120"}


class EmailCodeNotMatchError(APIException):
    status_code = 400
    default_detail = {"message": "이메일 인증 코드 또는 첨부된 이메일이 일치하지 않습니다.", "code": "0130"}


class EmailTimeoutError(APIException):
    status_code = 400
    default_detail = {"message": "이메일 인증 시간이 초과되었습니다.", "code": "0131"}


class EmailCodeNotMatchAfterAuthError(APIException):
    status_code = 400
    default_detail = {"message": "인증 시 사용된 코드(이메일)와 Body의 코드(이메일)가 일치하지 않습니다.", "code": "0132"}


class EmailCeleryError(APIException):
    status_code = 400
    default_detail = {"message": "이메일 발송 도중 문제가 발생했습니다.", "code": "0133"}


class UserExplainTooLong(APIException):
    status_code = 400
    default_detail = {"message": "유저의 자기소개 글이 너무 깁니다.", "code": "0140"}
