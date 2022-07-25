from django.shortcuts import render, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.contrib.auth.mixins import LoginRequiredMixin
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

from prepaid_meters_token_generator_system.user_permission_tests import is_admin, is_super_admin, is_admin_or_super_admin
from prepaid_meters_token_generator_system.mixins import SuperAdminRequiredMixin, AdminRequiredMixin, AdminOrSuperAdminRequiredMixin

from meter.externalAPI.notifications import NotificationImpl, TwilioSMSClient

from user.forms import SuperAdminCreateUserForm, AdminCreateUserForm, EditUserForm, EditUserProfileForm, RevokePasswordForm, ResetPasswordForm, ChangePasswordForm
from user.account_types import SUPER_ADMIN, ADMIN, MANAGER
from user.utils import EDIT, DELETE, is_forbidden_user_model_operation
from user.models import UnitPrice

# Create your views here.

User = get_user_model()


class UnitPriceEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnitPrice
    fields = "__all__"
    template_name = "user/register_price_per_unit.html.development"
    success_message = "Changes saved successfully"
    success_url = reverse_lazy("list_users")
    

class UserListView(AdminOrSuperAdminRequiredMixin, ListView):
    template_name = "user/list_accounts.html.development"
    context_object_name = "users"

    def get_queryset(self):
        account_type = self.request.user.account_type
        if account_type == SUPER_ADMIN:
            return User.objects.filter(Q(account_type=MANAGER) | Q(account_type=ADMIN))
        else:
            return User.objects.filter(Q(account_type=MANAGER))
        

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
        if self.request.user.account_type == SUPER_ADMIN:
            return SuperAdminCreateUserForm
        else:
            return AdminCreateUserForm

    def get_success_message(self, cleaned_data):
        # Make the meter number accessible in the success_message
        designation = "Manager"
        if cleaned_data["account_type"] == ADMIN:
            designation = "Administrator"
        return self.success_message % dict(
            cleaned_data,
            designation=designation
        )

    def form_valid(self, form):
        self.object = form.save()
        user = self.object
        if user.account_type == MANAGER:
            # Only managers can a have unitprice field
            unit_price = UnitPrice.objects.create(manager=user)
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return HttpResponseRedirect(self.get_success_url())
    
    

class UserEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = EditUserForm
    success_message = "Changes saved successfully"

    def get_success_url(self):
        return reverse_lazy("list_users")

    def post(self, request, *args, **kwargs):
        user_being_edited = self.get_object()
        """
        Prevent admins from deleting fellow admins and super admins and likewise,
        prevent super admins from editing fellow super admins
        """
        edit_user_operation_caller = request.user
        edit_user_operation_callee = user_being_edited
        edit_operation = (EDIT, edit_user_operation_caller, edit_user_operation_callee)
        
        if is_forbidden_user_model_operation(edit_operation):
            raise PermissionDenied
        
        return super(UserEditView, self).post(request, *args, **kwargs)


class UserProfileEditView(LoginRequiredMixin, View):
    template_name = "user/profile.html.development"
    
    def post(self, *args, **kwargs):
        
        if self.is_password_update_request(self.request):
            return self.update_password(self.request.user)
        return self.update_personal_info(self.request.user)

    def is_password_update_request(self, request):
        return (request.POST.get("current_password") and request.POST.get("new_password"))

    def update_personal_info(self, user):
        success_message = "Changes saved successfully"
        self.edit_user_profile_form = EditUserProfileForm(self.request.POST, instance=user)
        self.change_password_form = ChangePasswordForm(user=user) # The profile template requires it
        
        if self.edit_user_profile_form.is_valid():
            self.edit_user_profile_form.save()
            messages.success(self.request, success_message)

        context = self.get_context()
        return render(self.request, self.template_name, context)

    def update_password(self, user):
        success_message = "Password succesfully changed"
        self.edit_user_profile_form = EditUserProfileForm(user=user) # The profile template requires it
        self.change_password_form = ChangePasswordForm(self.request.POST, user=user)

        if self.change_password_form.is_valid():
            self.change_password_form.update_password()
            messages.success(self.request, success_message)

        context = self.get_context()
        return render(self.request, self.template_name, context)

    def get_context(self):
        context = {
            "edit_user_profile_form": self.edit_user_profile_form,
            "change_password_form": self.change_password_form,
        }
        return context

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse("profile"))
    
    
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
    if not is_action_allowed(request.user.account_type, user):
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
    user_to_be_deleted = get_object_or_404(User, pk=pk)
    # Prevent admins from deleting super admin and fellow admin accounts and likewise super admins from deleting fellow super admin accounts
    delete_operation_caller = request.user
    delete_operation_callee = user_to_be_deleted
    delete_operation = (DELETE, delete_operation_caller, delete_operation_callee)
    if is_forbidden_user_model_operation(delete_operation):
        raise PermissionDenied
    
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
                
            # Donot alert the user about users that donot exist
            messages.success(self.request, "SMS with password reset instructions has been sent.")
            return render(self.request, "user/reset_password.html.development", {"form": reset_password_form})
    
    
@login_required
def dashboard(request):
    return render(request, "user/dashboard.html.development")


@login_required
def profile(request):
    user = request.user
    edit_user_profile_form = EditUserProfileForm(user=user)
    change_password_form = ChangePasswordForm(user=user)
    context = {
        "edit_user_profile_form": edit_user_profile_form,
        "change_password_form": change_password_form,
    }
    return render(request, "user/profile.html.development", context)
