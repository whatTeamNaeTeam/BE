from rest_framework.pagination import PageNumberPagination, CursorPagination


class ListPagenationSize10(PageNumberPagination):
    page_size = 10


class TeamPagination(CursorPagination):
    page_size = 2
    ordering = "created_at"
