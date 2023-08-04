from django.contrib.auth import get_user_model
from django.db.models import Q

from rest_framework.generics import ListAPIView

from .serializers import UserSerializer
from .api_permissions import IsAdminOrSuperAdmin

User = get_user_model()


class UserListAPIView(ListAPIView):
    queryset = User.objects.all_managers()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        query = self.request.GET.get("q")
        return super().get_queryset().filter(Q(first_name__icontains=query) | Q(last_name__icontains=query))
