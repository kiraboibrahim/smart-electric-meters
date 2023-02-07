from shared.forms import SearchForm as MeterSearchForm
from shared.utils.paginator import paginate_queryset
from .utils import get_user_meters


class MetersContextMixin(object):
    page_url_kwarg = "page"
    """
    Allow views that use the list_meters template to access the  paginator, page_obj, meters context variables
    """
    def _get_page_number(self):
        try:
            page_number = int(self.request.GET.get(self.page_url_kwarg, 1))
        except ValueError:
            page_number = 1
        return page_number

    def get_meters_context(self):
        meters = get_user_meters(self.request.user).filter(is_active=True)
        paginator = paginate_queryset(meters)
        page_obj = paginator.get_page(self._get_page_number())
        context = {
            "paginator": paginator,
            "page_obj": page_obj,
            "meters": page_obj.object_list,
            "meter_search_form": MeterSearchForm(self.request.GET)
        }
        return context
