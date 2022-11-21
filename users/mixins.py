from shared.utils.paginator import paginate_queryset

from .utils import get_users


class UsersContextMixin(object):
    """
    Allow views that use the list_users template to access the  paginator, page_obj, users context variables
    """
    def get_page_number(self):
        try:
            page_number = int(self.request.GET.get("page", 1))
        except ValueError:
            page_number = 1
        return page_number

    def get_users_context(self):
        context = {}

        user = self.request.user
        users = get_users(user)
        paginator = paginate_queryset(users)
        page_obj = paginator.get_page(self.get_page_number())
        context["paginator"] = paginator
        context["page_obj"] = page_obj
        context["users"] = page_obj.object_list
        return context
