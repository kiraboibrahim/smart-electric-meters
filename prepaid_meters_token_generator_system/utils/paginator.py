from django.core.paginator import Paginator, PageNotAnInteger


def paginate_queryset(queryset, page_size):
    paginator = Paginator(queryset, page_size)
    return paginator


def get_page_number(request, page_kwarg = "page"):
    try:
        page_number = int(request.GET.get("page", "1"))
    except ValueError:
        raise PageNotAnInteger()
    return page_number
