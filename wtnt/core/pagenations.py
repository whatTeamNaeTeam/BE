from rest_framework.pagination import PageNumberPagination, CursorPagination
import wtnt.settings as api_settings


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


class TeamPagination(CursorPagination):
    page_size = 2
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
