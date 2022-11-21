from django.core.exceptions import ImproperlyConfigured

from search_views.filters import build_q


class SearchMixin(object):
    search_field_mapping = None

    def get_field_mapping(self):
        if self.search_field_mapping is None:
            raise ImproperlyConfigured("search_field_mapping is not defined")
        return self.search_field_mapping

    def get_search_filters(self):
        search_filters = build_q(self.get_field_mapping().get_search_fields(), self.request.GET)
        return search_filters
