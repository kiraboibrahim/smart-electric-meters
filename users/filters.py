from search_views.filters import BaseFilter


class UserSearchUrlQueryKwargMapping(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["first_name", "last_name"]
        }
    }
