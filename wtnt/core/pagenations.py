from rest_framework.pagination import PageNumberPagination


class ListPagenationSize10(PageNumberPagination):
    page_size = 10
