from django.views.generic.list import ListView
from django.core.exceptions import ImproperlyConfigured

from search_views.filters import build_q


class SearchListView(ListView):
    model_list_filter_class = None
    search_query_parameter_mapping_class = None
    http_method_names = ["get"]

    def get_model_list_filter_class(self):
        return self.model_list_filter_class

    def get_queryset(self):
        queryset = super().get_queryset()
        filters = build_q(self.get_search_query_parameter_mapping_class().get_search_fields(), self.request.GET)
        queryset = queryset.filter(filters)
        # Filter search results based on model fields if specified
        model_fields_filter_class = self.get_model_list_filter_class()
        if model_fields_filter_class is not None:
            queryset = self.model_list_filter_class(self.request.GET, queryset=queryset).qs
        return queryset

    def get_search_query_parameter_mapping_class(self):
        if self.search_query_parameter_mapping_class is None:
            raise ImproperlyConfigured("search_query_parameter_mapping_class attribute is missing")
        return self.search_query_parameter_mapping_class


class FilterListView(ListView):
    model_list_filter_class = None
    http_method_names = ["get"]

    def get_queryset(self):
        queryset = self.get_model_list_filter_class()(self.request.GET, queryset=super().get_queryset()).qs
        return queryset
    
    def get_model_list_filter_class(self):
        if self.model_list_filter_class is None:
            raise ImproperlyConfigured("model_fields_filter_class attribute is missing")
        return self.model_list_filter_class
