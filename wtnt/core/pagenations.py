from rest_framework.pagination import PageNumberPagination, CursorPagination
from django.core.paginator import Paginator
import wtnt.settings as api_settings

from django.core.cache import cache


class ListPagenationSize10(PageNumberPagination):
    page_size = 10

    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri(self.page.next_page_number())
        if api_settings.DEBUG:
            return url
        return url.replace("http://localhost:8000", api_settings.MY_DOMAIN)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri(self.page.previous_page_number())
        if api_settings.DEBUG:
            return url
        return url.replace("http://localhost:8000", api_settings.MY_DOMAIN)


class CachedPaginator(Paginator):
    def __init__(self, *args, cache_key=None, cache_timeout=600, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_key = cache_key
        self.cache_timeout = cache_timeout

    @property
    def count(self):
        if self.cache_key:
            cached_count = cache.get(self.cache_key)
            if cached_count is not None:
                return cached_count

        count = super().count

        if self.cache_key:
            cache.set(self.cache_key, count, timeout=self.cache_timeout)

        return count


class UserListPagenationSize10(ListPagenationSize10):
    def paginate_queryset(self, queryset, request, view=None, is_search=None):
        self.request = request
        cache_key = "" if is_search else "cached_count_user"
        paginator = CachedPaginator(queryset, self.page_size, cache_key=cache_key, cache_timeout=60 * 10)
        self.page = paginator.page(self.request.query_params.get("page", 1))

        return list(self.page)


class TeamListPagenationSize10(ListPagenationSize10):
    def paginate_queryset(self, queryset, request, view=None, is_search=None):
        self.request = request
        cache_key = "" if is_search else "cached_count_team"
        paginator = CachedPaginator(queryset, self.page_size, cache_key=cache_key, cache_timeout=60 * 10)
        self.page = paginator.page(self.request.query_params.get("page", 1))

        return list(self.page)


class TeamPagination(CursorPagination):
    page_size = 4
    ordering = "-created_at"

    def get_next_link(self):
        url = super().get_next_link()
        if url:
            if api_settings.DEBUG:
                return url
            return url.replace("http://localhost:8000", api_settings.MY_DOMAIN)
        return None

    def get_previous_link(self):
        url = super().get_previous_link()
        if url:
            if api_settings.DEBUG:
                return url
            return url.replace("http://localhost:8000", api_settings.MY_DOMAIN)
        return None
