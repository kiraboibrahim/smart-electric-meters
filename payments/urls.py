from django.urls import path

import payments.views as payment_views


urlpatterns = [
    path("receive-callback-POK8ioBRLlhYdw", payment_views.PaymentCallbackView.as_view(), name="callback_receive"),
]
