from rest_framework import serializers

from .models import Meter


class MeterSerializer(serializers.ModelSerializer):

    class Meta:
        model = Meter
        fields = ["meter_number", "manager", "vendor", "due_fees", "is_active", "created_at", "manager_unit_price"]
