from .models import Payment


def get_user_payments(user, initial_payments=None):
    payments = initial_payments if initial_payments is not None else Payment.objects.all()
    if user.is_manager():
        payments = payments.filter(user=user)
    return payments
