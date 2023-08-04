import django.dispatch


payment_successful = django.dispatch.Signal()
payment_failed = django.dispatch.Signal()
