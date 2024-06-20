from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import exception_handler


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


class VersionError(APIException):
    status_code = 400
    default_detail = "Version Not Matched"

    def __init__(self, current_version):
        self.default_detail = {"detail": self.default_detail, "version": current_version}
        super().__init__(detail=self.default_detail, code=self.default_code)


class Custom400Error(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class Custom500Error(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        response = Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    if isinstance(exc, Custom400Error):
        response.status_code = status.HTTP_400_BAD_REQUEST
        response.data = {"detail": str(exc)}

    if isinstance(exc, Custom500Error):
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        response.data = {"detail": str(exc)}

    return response
