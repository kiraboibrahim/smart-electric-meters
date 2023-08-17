from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ["first_name", "last_name", "email", "address", "phone_no", "account_type"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["phone_no"] = instance.phone_no.national_number  # Strip off the plus & country code i.e. +256
        return ret
