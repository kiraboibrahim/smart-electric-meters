
from django import forms
from django.core.exceptions import ImproperlyConfigured

class BaseFiltersForm(forms.Form):

    def get_filters(self):
        filters = {}
        if self.is_valid():
            for field, value in self.cleaned_data.items():
                if value is None or value == '':
                    continue
                filters[field] = value
        return filters


class BaseSearchForm(forms.Form):
    q = forms.CharField(required=True) # Query string
    model_search_field = None

    def get_filters(self):
        filters = {}
        if self.is_valid():
            query_string = self.cleaned_data.get("q")
            if isinstance(self.model_search_field, forms.ChoiceField):
                model_search_field = self.cleaned_data.get("model_search_field")
                model_search_field = "{}__contains".format(model_search_field)
                filters[model_search_field] = query_string
            elif isinstance(self.model_search_field, str):
                model_search_field = "{}__contains".format(self.model_search_field)
                filters[model_search_field] = query_string
            else:
                raise ImproperlyConfigured("model_search_field can either be a string or django.forms.ChoiceField")
        return filters
