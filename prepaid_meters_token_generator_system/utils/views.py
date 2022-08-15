from django.core.exceptions import ImproperlyConfigured
from django.views.generic.list import ListView


class FiltersListView(ListView):
    
    filters_form_class = None
    filters_form = None

    def get_filters_form_class(self):
        if self.filters_form_class is None:
            raise ImproperlyConfigured("The filters_form_class is missing")
        return self.filters_form_class
    
    def get_filters(self):
        filters = {}
        filters_form_class = self.get_filters_form_class()
        filters_form = filters_form_class(self.request.GET) # Bind the form to the GET Parameters

        self.filters_form = filters_form

        filters = filters_form.get_filters()

        self.filters = filters

        return filters

    def get_queryset(self):
        filters = self.get_filters()
        return super(FiltersListView, self).get_queryset().filter(**filters)


    def get_filters_form(self):
        if self.filters_form is None:
            # Form has not been bounded, return Unbound Form
            filters_form_class = self.get_filters_form_class()
            filters_form  = filters_form_class()
        else:
            filters_form = self.filters_form
        return filters_form

    def get_request_parameter_string(self):
        filters_form = self.get_filters_form()
        request_parameter_string = filters_form.get_request_parameter_string()
        return request_parameter_string
        
    def get_context_data(self, **kwargs):
        context = super(FiltersListView, self).get_context_data(**kwargs)
        filters_form = self.get_filters_form()
        request_parameter_string = self.get_request_parameter_string()

        context["filters_form"] = filters_form
        context["request_parameter_string"] = request_parameter_string
        
        return context


class SearchListView(ListView):
    search_form_class = None
    search_form = None

    # Allow filtering search results
    filters_form_class = None
    filters_form = None

    def get_search_form_class(self):
        if self.search_form_class is None:
            raise ImproperlyConfigured("search_form_class is missing")
        return self.search_form_class

    def get_filters(self):
        filters = {}
        if self.filters_form_class is not None:
            filters_form = self.filters_form_class(self.request.GET)

            self.filters_form = filters_form

            filters = filters_form.get_filters()
        return filters
        
    def get_predicates(self):
        predicates = {}
        search_form_class = self.get_search_form_class()
        search_form = search_form_class(self.request.GET) # Bind the form to the GET Parameters

        self.search_form = search_form
        
        predicates = search_form.get_predicates()
        self.predicates = predicates
        return predicates

    def get_queryset(self):
        predicates = self.get_predicates()
        filters = self.get_filters()
        qs = super(SearchListView, self).get_queryset().filter(**predicates, **filters)
        return qs


    def get_request_parameter_string(self):
        request_parameter_string = self.search_form.get_request_parameter_string()

        if self.filters_form is not None:
            request_parameter_string_for_filters = self.filters_form.get_request_parameter_string()
            if request_parameter_string_for_filters:
                request_parameter_string = "{}&{}".format(request_parameter_string, request_parameter_string_for_filters)
        return request_parameter_string

        
    def get_context_data(self, **kwargs):
        context = super(SearchListView, self).get_context_data(**kwargs)

        filters_form = None

        if self.filters_form:
            filters_form = self.filters_form

        context["search_form"] = self.search_form
        context["filters_form"] = filters_form
        context["request_parameter_string"] = self.get_request_parameter_string()
        
        return context
