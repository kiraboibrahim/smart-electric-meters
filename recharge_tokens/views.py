from django.views.generic.list import ListView
from django.conf import settings

from .models import RechargeToken


class RechargeTokenListView(ListView):
    model = RechargeToken
    template_name = "recharge_tokens/list_recharge_tokens.html.development"
    paginate_by = settings.MAX_ITEMS_PER_PAGE
