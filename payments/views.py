import logging

from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from core.services.payment.backends.payleo.utils import parse_callback_response, allow_only_payleo_ip

from .models import Payment

logger = logging.getLogger(__name__)


@method_decorator(allow_only_payleo_ip, "dispatch")
@method_decorator(csrf_exempt, "dispatch")
class PaymentCallbackView(TemplateResponseMixin, View):
    SUCCESSFUL_METHOD = "receivePayment"
    FAILED_METHOD = "notifyFailedPayment"

    content_type = "text/xml"
    template_name = "payments/callback_response.xml"

    def dispatch(self, request, *args, **kwargs):
        self.callback_response = parse_callback_response(request.body)
        super().dispatch(request, *args, **kwargs)

    def http_method_not_allowed(self, request, *args, **kwargs):
        """The HTTP method used by the API to send the callback response isn't document, so to excuse ourselves
        from this predicament, we override the method called when the HTTP method isn't supported"""
        return self.post(request, *args, **kwargs)

    def get_object(self):
        obj = Payment.objects.get(external_id=self.callback_response["transaction_id"])
        return obj

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
            if self.callback_response["method"] == self.SUCCESSFUL_METHOD:
                self.object.mark_as_successful()
            else:
                self.object.mark_as_failed(reason=self.callback_response["failure_reason"])
        except Exception:
            logger.exception("Payment callback processing failure")
            pass  # We should acknowledge receipt of callback irrespective of any exception that occurred while processing it
        return self.render_to_response(context={})

    def render_to_response(self, context, **response_kwargs):
        content = loader.render_to_string(self.get_template_names()).encode("utf-8")
        return HttpResponse(content=content, content_type=self.content_type)
