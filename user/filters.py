from search_views.filters import BaseFilter
import django_filters


class UserSearchFilter(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["first_name", "last_name"]
        }
    }
