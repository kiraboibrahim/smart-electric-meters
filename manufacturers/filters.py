from search_views.filters import BaseFilter


class MeterManufacturerSearchUrlQueryKwargMapping(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["name"]
        }
    }
