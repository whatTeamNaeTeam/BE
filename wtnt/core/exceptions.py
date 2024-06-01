from rest_framework.exceptions import APIException


class IsNotLeaderError(APIException):
    status_code = 403
    default_detail = "It's not leader of team"


class IsNotOwnerError(APIException):
    status_code = 403
    default_detail = "It's not an owner"


class CodeNotMatchError(APIException):
    status_code = 400
    default_detail = "Code Not Matched"


class RefreshTokenExpiredError(APIException):
    status_code = 401
    default_detail = "Expired Refresh Token"


class CeleryTaskError(APIException):
    status_code = 400
    default_detail = ""


class NotFoundError(APIException):
    status_code = 404
    default_detail = "No Content"


class SerializerNotValidError(APIException):
    status_code = 400
    default_detail = ""

    @staticmethod
    def get_detail(error_dict):
        error_messages = ""
        for field, errors in error_dict.items():
            for error in errors:
                error_messages += f"{field}: {error}\n"

        return error_messages


class KeywordNotMatchError(APIException):
    status_code = 400
    default_datail = "Keyword Not Matched"


class ClosedApplyError(APIException):
    status_code = 400
    default_detail = "It's a closed apply"


class DuplicatedApplyError(APIException):
    status_code = 400
    default_detail = "It's a duplicated apply"
