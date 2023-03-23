from django.views.generic.detail import SingleObjectMixin
from django.core.exceptions import PermissionDenied


class MeterCategorySingleObjectMixin(SingleObjectMixin):
    def get_object(self, queryset=None):
        meter_category = super().get_object(queryset)
        if meter_category.is_default():
            raise PermissionDenied
        return meter_category