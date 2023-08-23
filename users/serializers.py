from django.contrib.auth import get_user_model

from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = get_user_model()
        fields = ["id", "first_name", "last_name", "email", "address", "phone_no"]

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret["phone_no"] = f"{instance.phone_no}"
        return ret
