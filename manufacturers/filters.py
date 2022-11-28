from search_views.filters import BaseFilter


class MeterManufacturerSearchQueryParameterMapping(BaseFilter):
    search_fields = {
        "query": {
            "operator": "__icontains",
            "fields": ["name"]
        }
    }
