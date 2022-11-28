from .models import RechargeToken


def get_user_recharge_tokens(user, initial_recharge_tokens=None):
    recharge_tokens = initial_recharge_tokens if initial_recharge_tokens is not None else RechargeToken.objects.all()
    if user.is_manager():
        # Show only recharge tokens for the manager's meters
        recharge_tokens = recharge_tokens.filter(meter__in=user.meters.all())
    return recharge_tokens
