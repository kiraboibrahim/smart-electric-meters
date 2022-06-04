from django.shortcuts import render, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import View

from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin, SuperAdminRequiredMixin, AdminRequiredMixin, AdminOrSuperAdminRequiredMixin
from meter.api import NotificationImpl, TwilioSMSClient
from user.forms import SuperAdminCreateUserForm, EditUserForm, AdminCreateUserForm, RevokePasswordForm, ResetPasswordForm
from user.acc_types import SUPER_ADMIN, ADMIN, MANAGER
from user.utils import is_action_allowed
from user.models import PricePerUnit

# Create your views here.

User = get_user_model()


class PricePerUnitCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = PricePerUnit
    template_name = "user/register_price_per_unit.html.development"
    fields = "__all__"
    success_url = reverse_lazy("set_price_per_unit")
    success_message = "Price registered successfully."
    

class UserListView(AdminOrSuperAdminRequiredMixin, ListView):
    template_name = "user/list_accounts.html.development"
    context_object_name = "users"

    def get_queryset(self):
        user_type = self.request.user.acc_type
        if user_type == SUPER_ADMIN:
            return User.objects.filter(Q(acc_type=MANAGER) | Q(acc_type=ADMIN))
        else:
            return User.objects.filter(Q(acc_type=MANAGER))
        

class UserCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    template_name = "user/create_user.html.development"
    model = User
    success_message = "%(designation)s: %(first_name)s %(last_name)s has been registered successfully"
    success_url = reverse_lazy("create_user")

    def get_form_class(self):
        """ 
        Admins and Super Admins have different privileges in account creation.
        Admins can create managers only and while super admins can create both admins and managers.
        The above privileges have been discerned with the use of different forms.
        """
        if self.request.user.acc_type == SUPER_ADMIN:
            return SuperAdminCreateUserForm
        else:
            return AdminCreateUserForm

    def get_success_message(self, cleaned_data):
        # Make the meter number accessible in the success_message
        designation = "Manager"
        if cleaned_data["acc_type"] == ADMIN:
            designation = "Administrator"
        return self.success_message % dict(
            cleaned_data,
            meter_no=self.object.meter_no,
            designation=designation
        )
    
    

class UserEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    template_name = "user/edit_user.html.development"
    form_class = EditUserForm
    success_message = "Changes saved successfully"

    def get_success_url(self):
        return reverse_lazy("edit_user", kwargs={"pk": self.object.id})

    def post(self, request, *args, **kwargs):
        
        user = self.get_object() # The user being edited
        """
        Prevent admins from deleting fellow admins and super admins and likewise,
        prevent super admins from editing fellow super admins
        """
        if not is_action_allowed(request.user.acc_type, user):
            raise PermissionDenied
        
        return super(UserEditView, self).post(request, *args, **kwargs)

@user_passes_test(is_admin_or_super_admin)
def revoke_password(request, pk):
    """ 
    Revoking a password requires active sessions of admins and super admins 
    """
    
    user = get_object_or_404(User, pk=pk)
    """
    Donot allow admins to revoke super admin and fellow admin accounts passwords and likewise stop super 
    admins from revoking passwords of fellow super admins
    """
    if not is_action_allowed(request.user.acc_type, user):
        raise PermissionDenied
    
    # Name of account whose password will be revoked
    full_name = "%s %s" %(user.first_name, user.last_name)
    if request.method == "POST":
        form = RevokePasswordForm(request.POST, user=user)
        if form.is_valid():
            form.revoke_password()
            messages.success(request, "Password has been changed.")
        return render(request, "user/revoke_password.html.development", {"form": form, "full_name": full_name})
    else:
        form = RevokePasswordForm()
        return render(request, "user/revoke_password.html.development", {"form": form, "full_name": full_name})


@user_passes_test(is_admin_or_super_admin)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    # Prevent admins from deleting super admin and fellow admin accounts and likewise super admins from deleting fellow super admin accounts
    if not is_action_allowed(request.user.acc_type, user):
        raise PermissionDenied
    # Delete user 
    user.delete()
    full_name = "%s %s" %(user.first_name, user.last_name)
    messages.success(request, "User: %s deleted successfully" %(full_name))
    return HttpResponseRedirect(reverse("list_users"))


def send_sms(source, destination, message):
    sms_client = TwilioSMSClient(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    notification = NotificationImpl(sms_client)
    notification.send(source, destination, message)
                

def get_context_for_password_reset(user):
    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.id))

    # Context for the reset password sms 
    context = {
        "site_name": "LEGIT SYSTEMS",
        "protocol": "http",
        "domain": "localhost:8000",
        "uid": uidb64,
        "token": token,
    }
    return context



class ResetPassword(View):

    def get(self, *args, **kwargs):
        reset_password_form = ResetPasswordForm()
        return render(self.request, "user/reset_password.html.development", {"form": reset_password_form})


    def post(self, *args, **kwargs):
        reset_password_form = ResetPasswordForm(self.request.POST)
        message_template = "user/reset_password_sms.txt.development"
        
        if reset_password_form.is_valid():
            user_id = kwargs.get("pk")
            phone_no = reset_password_form.cleaned_data.get("phone_no")
            user = User.objects.get(phone_no=phone_no)
            if user:
                context = get_context_for_password_reset(user)
                message = render_to_string(message_template, context)
                source = settings.TWILIO_PHONE_NO
                destination = "%s%s" %("+256", phone_no[1:])
                send_sms(source, destination, message)
                
            # Donot alert users of non existent accounts
            messages.success(self.request, "SMS with password reset instructions has been sent.")
            return render(self.request, "user/reset_password.html.development", {"form": reset_password_form})
    
    
@login_required
def profile(request):
    return render(request, "user/profile.html.development")
