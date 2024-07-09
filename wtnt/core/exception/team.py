from rest_framework.exceptions import APIException


class TeamNameLengthError(APIException):
    status_code = 400
    default_detail = {"message": "팀 이름이 공백이거나 길이가 맞지 않습니다.", "code": "0200"}


class TeamGenreNotValidError(APIException):
    status_code = 400
    default_detail = {"message": "프로젝트의 유형이 올바르지 않습니다.", "code": "0210"}


class TeamCategoryNotValidError(APIException):
    status_code = 400
    default_detail = {"message": "정해진 범주 내의 서브 카테고리가 아닙니다.", "code": "0220"}


class TeamMemberCountLengthError(APIException):
    status_code = 400
    default_detail = {"message": "모집인원의 숫자가 적절하지 못합니다.", "code": "0221"}


class TeamExplainLengthError(APIException):
    status_code = 400
    default_detail = {"message": "프로젝트 설명이 공백이거나 길이를 넘어섰습니다.", "code": "0230"}


class TeamUrlLengthError(APIException):
    status_code = 400
    default_detail = {"message": "프로젝트 관련 URL이 공백입니다.", "code": "0240"}


class TeamImageTypeError(APIException):
    status_code = 400
    default_detail = {"message": "파일이 이미지가 아니거나 지원하지 않는 형식입니다", "code": "0250"}


class TeamKeywordNotMatchError(APIException):
    status_code = 400
    default_detail = {"message": "검색에 필요한 키워드가 아닙니다.", "code": "0260"}
