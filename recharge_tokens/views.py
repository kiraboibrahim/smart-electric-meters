from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin

from shared.forms import SearchForm as RechargeTokenSearchForm
from shared.views import FilterListView, SearchListView

from .models import RechargeToken
from .filters import RechargeTokenListFilter, RechargeTokenSearchUrlQueryKwargMapping
from .forms import RechargeTokenFiltersForm
from .utils import get_user_recharge_tokens


class RechargeTokenListView(LoginRequiredMixin, FilterListView):
    model = RechargeToken
    template_name = "recharge_tokens/list_recharge_tokens.html.development"
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    context_object_name = "recharge_tokens"
    model_list_filter_class = RechargeTokenListFilter

    def get_template_names(self):
        if self.request.user.is_manager():
            return "managers/recharge_tokens/list_recharge_tokens.html.development"
        return self.template_name

    def get_queryset(self):
        recharge_tokens = super().get_queryset().select_related()
        return get_user_recharge_tokens(self.request.user, initial_recharge_tokens=recharge_tokens)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recharge_token_filters_form"] = RechargeTokenFiltersForm(self.request.GET)
        context["recharge_token_search_form"] = RechargeTokenSearchForm(self.request.GET)
        return context


class RechargeTokenSearchView(LoginRequiredMixin, SearchListView):
    model = RechargeToken
    template_name = "recharge_tokens/list_recharge_tokens.html.development"
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    context_object_name = "recharge_tokens"

    search_url_query_kwarg_mapping_class = RechargeTokenSearchUrlQueryKwargMapping
    model_fields_filter_class = RechargeTokenListFilter

    def get_queryset(self):
        recharge_tokens = super().get_queryset().select_related()
        return get_user_recharge_tokens(self.request.user, initial_recharge_tokens=recharge_tokens)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["recharge_token_filters_form"] = RechargeTokenFiltersForm(self.request.GET)
        context["recharge_token_search_form"] = RechargeTokenSearchForm(self.request.GET)
        return context
