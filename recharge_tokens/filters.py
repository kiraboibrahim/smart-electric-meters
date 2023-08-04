from django import forms
from django.contrib.auth import get_user_model

import django_filters

from core.widgets import DateInput
from .models import RechargeTokenOrder

User = get_user_model()


class RechargeTokenOrderFilter(django_filters.FilterSet):
    order_id = django_filters.CharFilter(field_name="id", lookup_expr="icontains", label="Order ID")
    manager = django_filters.ChoiceFilter(field_name="meter__manager", lookup_expr="exact", label="Manager")
    from_ = django_filters.DateFilter(field_name="placed_at", lookup_expr="gt", label="From")
    to = django_filters.DateFilter(field_name="placed_at", lookup_expr="lt", label="To")

    class Meta:
        model = RechargeTokenOrder
        fields = ("order_id", "manager", "from_", "to")

    def get_form_class(self):
        base_form_class = super().get_form_class()

        class FormClass(base_form_class):
            from_ = forms.DateField(widget=DateInput(), required=False)
            to = forms.DateField(widget=DateInput(), required=False)
            if self.request.user.is_admin() or self.request.user.is_super_admin():
                manager = forms.ModelChoiceField(queryset=User.objects.all_managers(), required=False)
            else:
                manager = None

        return FormClass

    @property
    def qs(self):
        orders = super().qs
        return orders.for_user(self.request.user)
