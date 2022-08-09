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
            if filters_form.is_valid():
                # Attach the bound form to the view so that it is accessible when getting context_data
                self.filters_form = filters_form
                filters = filters_form.get_applied_filters()
        return filters

    def get_queryset(self):
        filters = self.get_filters()
        return super(FiltersListView, self).get_queryset().filter(**filters)

    def get_context_data(self, **kwargs):
        context = super(FiltersListView, self).get_context_data(**kwargs)
        if self.filters_form is None:
            # Form has not been bounded, return Unbound Form
            context["filters_form"] = self.get_filters_form_class()
        else:
            context["filters_form"] = self.filters_form
        return context
