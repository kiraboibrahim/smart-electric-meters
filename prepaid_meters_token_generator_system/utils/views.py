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

        if self.request.GET:
            filters_form = filters_form_class(self.request.GET) # Bind the form to the GET Parameters
            self.filters_form = filters_form
            filters = filters_form.get_filters()
            self.filters = filters
        return filters

    def get_queryset(self):
        filters = self.get_filters()
        return super(FiltersListView, self).get_queryset().filter(**filters)

    def get_filters_string(self):
        filters_list = []
        filters_string = ""
        if self.filters_form:
            filters_form_fields = self.filters_form.declared_fields
            for key, value in self.request.GET.items():
                # Exclude GET parameters that are not part of the filters form fields
                if key in filters_form_fields:
                    filters_list.append("{}={}".format(key, value))
        filters_string = "&".join(filters_list)
        return filters_string
                    
        
    def get_context_data(self, **kwargs):
        context = super(FiltersListView, self).get_context_data(**kwargs)
        if self.filters_form is None:
            # Form has not been bounded, return Unbound Form
            context["filters_form"] = self.get_filters_form_class()
        else:
            context["filters_form"] = self.filters_form
            
        context["filters_string"] = self.get_filters_string
        return context


class SearchListView(FiltersListView):
    search_form_class = None
    search_form = None

    def get_search_form_class(self):
        if self.search_form_class is None:
            raise ImproperlyConfigured("search_form_class is missing")
        return self.search_form_class
        
    def get_search_filters(self):
        filters = {}
        search_form_class = self.get_search_form_class()

        if self.request.GET:
            search_form= search_form_class(self.request.GET) # Bind the form to the GET Parameters
            self.search_form = search_form
            filters = search_form.get_filters()
            self.filters = filters
        return filters

    def get_queryset(self):
        search_filters = self.get_search_filters()
        field_filters = {}
        # If field filters have also been applied
        if self.filters_form_class is not None:
            field_filters = super().get_filters() 

        return super().get_queryset().filter(**search_filters, **field_filters)

    def get_filters_string(self):
        filters_list = []
        filters_string = ""
        if self.search_form:
            search_form_fields = self.search_form.declared_fields
            for key, value in self.request.GET.items():
                # Exclude GET parameters that are not part of the filters form fields
                if key in search_form_fields:
                    filters_list.append("{}={}".format(key, value))
        filters_string = "&".join(filters_list)
        return filters_string
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.search_form is None:
            # Form has not been bounded, return Unbound Form
            context["search_form"] = self.get_search_form_class()
        else:
            context["search_form"] = self.search_form

        filters_string = self.get_filters_string()
        if super().get_filters_string():
            filters_string = "{}&{}".format(filters_string, super().get_filters_string())
        
        context["filters_string"] = filters_string
        return context
