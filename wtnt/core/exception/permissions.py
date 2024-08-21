from rest_framework.exceptions import PermissionDenied


class IsNotApprovedUserError(PermissionDenied):
    default_detail = {"message": "인증된 회원의 요청이 아닙니다.", "code": "0300"}


class IsNotAdminUSerError(PermissionDenied):
    default_detail = {"message": "관리자의 요청이 아닙니다.", "code": "0301"}


class IsNotLeaderError(PermissionDenied):
    default_detail = {"message": "팀장의 요청이 아닙니다.", "code": "0302"}


class IsNotOwnerError(PermissionDenied):
    default_detail = {"message": "프로필 주인의 요청이 아닙니다.", "code": "0303"}


class IsNotInTeam(PermissionDenied):
    default_detail = {"meesage": "팀에 속해있지 않은 유저의 요청입니다.", "code": "0304"}
