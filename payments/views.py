from xml.dom.minidom import parseString

from django.views import View
from django.views.generic.base import TemplateResponseMixin
from django.http import HttpResponse
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from .models import Payment


@method_decorator(csrf_exempt, "dispatch")
class PaymentCallbackView(TemplateResponseMixin, View):
    SUCCESSFUL_METHOD_NAME = "receivePayment"
    FAILED_METHOD_NAME = "notifyFailedPayment"

    content_type = "text/xml"
    template_name = "payments/callback_response.xml"

    def http_method_not_allowed(self, request, *args, **kwargs):
        """The HTTP method used by the API to send the callback response isn't document, so to excuse ourselves
        from this predicament, we override the method called when the HTTP method isn't supported"""
        return self.post(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        method_name, external_payment_id, failure_reason = self.parse_request_body()
        payment = Payment.objects.get(external_id=external_payment_id)
        if method_name == self.SUCCESSFUL_METHOD_NAME:
            payment.mark_as_successful()
        else:
            payment.mark_as_failed(reason=failure_reason)
        return self.render_to_response(context={})

    def parse_request_body(self):
        callback_response = parseString(self.request.body.decode("utf-8").lstrip("\n").rstrip("\n"))
        method_name = callback_response.getElementsByTagName("method")[0].firstChild.data
        external_payment_id = callback_response.getElementsByTagName("transactionId")[0].firstChild.data
        try:
            failure_message = callback_response.getElementsByTagName("message")[0].firstChild.data
        except IndexError:
            failure_message = None
        return method_name, external_payment_id, failure_message

    def render_to_response(self, context, **response_kwargs):
        content = loader.render_to_string(self.get_template_names()).encode("utf-8")
        return HttpResponse(content=content, content_type=self.content_type)
