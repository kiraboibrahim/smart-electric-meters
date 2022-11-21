from django.core.paginator import Paginator, PageNotAnInteger

from django.conf import settings

PAGE_SIZE = settings.MAX_ITEMS_PER_PAGE


def paginate_queryset(queryset, page_size=PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    return paginator
