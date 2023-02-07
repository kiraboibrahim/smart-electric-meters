from django.conf import settings
from django.core.paginator import Paginator

PAGE_SIZE = settings.MAX_ITEMS_PER_PAGE


def paginate_queryset(queryset, page_size=PAGE_SIZE):
    paginator = Paginator(queryset, page_size)
    return paginator
