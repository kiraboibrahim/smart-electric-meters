import logging

from functools import wraps
from xml.dom.minidom import parseString

from django.core.exceptions import PermissionDenied

from .settings import PAYLEO_CALLBACK_IP

logger = logging.getLogger(__name__)


def parse_callback_response(response: bytes):
    response = response.decode("utf-8").lstrip("\n").rstrip("\n")
    doc = parseString(response)
    method = doc.getElementsByTagName("method")[0].firstChild.data
    msisdn = doc.getElementsByTagName("msisdn")[0].firstChild.data
    transaction_id = doc.getElementsByTagName("transactionId")[0].firstChild.data
    reference_id = doc.getElementsByTagName("referenceId")[0].firstChild.data
    amount = int(float(doc.getElementsByTagName("amount")[0].firstChild.data))
    client_transaction_id = None
    failure_reason = None
    try:
        client_transaction_id = doc.getElementsByTagName("client_transaction")[0].firstChild.data
    except (IndexError, AttributeError):
        pass
    try:
        failure_reason = doc.getElementsByTagName("message")[0].firstChild.data
    except (IndexError, AttributeError):
        pass
    return {
        "method": method,
        "msisdn": msisdn,
        "transaction_id": transaction_id,
        "reference_id": reference_id,
        "amount": amount,
        "client_transaction_id": client_transaction_id,
        "failure_reason": failure_reason
    }


def allow_only_payleo_ip(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        client_ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR")
        if client_ip != PAYLEO_CALLBACK_IP:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wraps(view_func)(_wrapped_view_func)
