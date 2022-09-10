from search_views.filters import BaseFilter


class MeterManufacturerSearchFilter(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["name"]
        }
    }
