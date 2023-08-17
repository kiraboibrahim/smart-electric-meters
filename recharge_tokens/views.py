from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from django_filters.views import FilterView

from .models import RechargeTokenOrder
from .filters import RechargeTokenOrderFilter


class RechargeTokenOrderListView(LoginRequiredMixin, FilterView):
    model = RechargeTokenOrder
    template_name = "recharge_tokens/recharge_token_order_list.html"
    paginate_by = settings.LEGIT_SYSTEMS_MAX_ITEMS_PER_PAGE
    context_object_name = "recharge_token_orders"
    filterset_class = RechargeTokenOrderFilter

