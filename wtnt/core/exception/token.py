from rest_framework.exceptions import AuthenticationFailed, PermissionDenied


class AccessTokenExpiredError(AuthenticationFailed):
    default_detail = {"message": "만료된 액세스 토큰입니다.", "code": "0400"}


class InvalidTokenError(PermissionDenied):
    default_detail = {"message": "유효한 토큰의 타입이 아닙니다.", "code": "0401"}


class AuthenticationHeaderSpaceError(PermissionDenied):
    default_detail = {"message": "인증 헤더는 반드시 두 덩이로 이루어져야합니다.", "code": "0402"}


class TokenWithNoUserDataError(PermissionDenied):
    default_detail = {"message": "토큰에 유저의 식별정보가 들어있지 않습니다.", "code": "0403"}


class UserNotFoundInTokenDataError(PermissionDenied):
    default_detail = {"message": "토큰의 유저 식별정보가 유효하지 않습니다.", "code": "0404"}


class UserInactiveInTokenDataError(PermissionDenied):
    default_detail = {"message": "토큰 속 유저가 Inactive 상태입니다.", "code": "0405"}


class NoTokenInAuthorizationHeaderError(PermissionDenied):
    default_detail = {"message": "자격 증명이 주어지지 않았습니다.", "code": "0406"}


class RefreshTokenExpiredError(AuthenticationFailed):
    default_detail = {"message": "리프레쉬 토큰이 만료되었습니다.", "code": "0410"}
