from payment.models import Payment

from user.account_types import MANAGER, ADMIN, SUPER_ADMIN

def get_payments(logged_in_user):
    if logged_in_user.account_type == ADMIN or logged_in_user.account_type == SUPER_ADMIN:
        return Payment.objects.all()
    elif logged_in_user.account_type == MANAGER:
        return Payment.objects.filter(user=logged_in_user)
    else:
        Payment.objects.none()
