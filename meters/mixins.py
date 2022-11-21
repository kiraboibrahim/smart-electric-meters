from .utils import get_user_meters

from shared.utils.paginator import paginate_queryset
from shared.forms import SearchForm as MeterSearchForm


class MetersContextMixin(object):
    """
    Allow views that use the list_meters template to access the  paginator, page_obj, meters context variables
    """
    def __get_page_number(self):
        try:
            page_number = int(self.request.GET.get("page", 1))
        except ValueError:
            page_number = 1
        return page_number

    def get_meters_context(self, user):
        meters = get_user_meters(user)
        meters = meters.filter(is_active=True)
        paginator = paginate_queryset(meters)
        page_obj = paginator.get_page(self.__get_page_number())
        context = {
            "paginator": paginator,
            "page_obj": page_obj,
            "meters": page_obj.object_list,
            "meter_search_form": MeterSearchForm(self.request.GET)
        }
        return context
