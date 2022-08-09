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
from django.views.generic import list as generic_list_views
from django.views.generic import edit as generic_edit_views
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import View
from django.core.mail import send_mail

from prepaid_meters_token_generator_system.utils.mixins import user_permissions as user_permission_mixins

from meter.externalAPI.notifications import NotificationImpl, TwilioSMSClient

from user import forms as user_forms
from user import account_types as user_account_types
from user import utils as user_utils
from user import models as user_models


User = get_user_model()


class UnitPriceEditView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.UpdateView):
    model = user_models.UnitPrice
    fields = "__all__"
    template_name = "user/register_price_per_unit.html.development"
    success_message = "Changes saved successfully"
    success_url = reverse_lazy("list_users")
    

class UserListView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, generic_list_views.ListView):
    template_name = "user/list_users.html.development"
    context_object_name = "users"
    paginate_by = 12;

    def get_queryset(self):
        logged_in_user = self.request.user
        return user_utils.get_users(logged_in_user)

    def get_context_data(self, **kwargs):
        context = super(UserListView, self).get_context_data(**kwargs)
        logged_in_user = self.request.user
        add_user_form_class = user_utils.get_add_user_form_class(logged_in_user)
        context["add_user_form"] = add_user_form_class()
        
        return context
        

class UserCreateView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.CreateView):
    model = User
    template_name = "user/list_users.html.development"
    success_message = "%(designation)s: %(first_name)s %(last_name)s has been added successfully"
    http_method_names = ["post"]
    
    def post(self, *args, **kwargs):
        return super(UserCreateView, self).post(*args, **kwargs)

    def get_form_class(self):
        logged_in_user = self.request.user
        return user_utils.get_add_user_form_class(logged_in_user)

    def get_success_message(self, cleaned_data):
        new_user_account_type = cleaned_data["account_type"]
        designation = "Manager"
        if new_user_account_type == user_account_types.ADMIN:
            designation = "Administrator"
            
        return self.success_message % dict(
            cleaned_data,
            designation=designation
        )

    def get_context_data(self, **kwargs):
        context= super(UserCreateView, self).get_context_data(**kwargs)
        context["add_user_form"] = context["form"]

        logged_in_user = self.request.user
        users = user_utils.get_users(logged_in_user)
        context["users"] = users
        return context
        
        

    def form_valid(self, form):
        self.object = form.save()
        user = self.object
        if user.account_type == MANAGER:
            # Only managers can a have unitprice field
            unit_price = UnitPrice.objects.create(manager=user)
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))
    
    

class UserEditView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, generic_edit_views.UpdateView):
    model = User
    template_name = "user/edit_user.html.development"
    form_class = user_forms.EditUserForm
    success_message = "Changes saved successfully"

    def get_success_url(self):
        return reverse_lazy("edit_user", kwargs={"pk": self.object.id})


    def get_context_data(self, **kwargs):
        context = super(UserEditView, self).get_context_data(**kwargs)
        logged_in_user = self.request.user
        context["users"] = user_utils.get_users(logged_in_user)

        return context
    
    def post(self, request, *args, **kwargs):
        user_being_edited = self.get_object()
        """
        Prevent admins from deleting fellow admins and super admins and likewise,
        prevent super admins from editing fellow super admins
        """
        edit_user_operation_caller = request.user
        edit_user_operation_callee = user_being_edited
        operation_type = user_utils.ModelOperations.EDIT
        edit_operation = (operation_type, edit_user_operation_caller, edit_user_operation_callee)
        
        if user_utils.is_forbidden_user_model_operation(edit_operation):
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
        self.edit_user_profile_form = user_forms.EditUserProfileForm(self.request.POST, instance=user)
        self.change_password_form = user_forms.ChangePasswordForm(user=user) # The profile template requires it
        
        if self.edit_user_profile_form.is_valid():
            self.edit_user_profile_form.save()
            messages.success(self.request, success_message)

        context = self.get_context()
        return render(self.request, self.template_name, context)

    def update_password(self, user):
        success_message = "Password succesfully changed"
        self.edit_user_profile_form = user_forms.EditUserProfileForm(user=user) # The profile template requires it
        self.change_password_form = user_forms.ChangePasswordForm(self.request.POST, user=user)

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
    

class UserDeleteView(user_permission_mixins.AdminOrSuperAdminRequiredMixin, View):
    
    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        user_to_be_deleted = get_object_or_404(User, pk=pk)
        
        delete_operation_caller = self.request.user
        delete_operation_callee = user_to_be_deleted
        operation_type = user_utils.ModelOperations.DELETE
        delete_operation = (operation_type, delete_operation_caller, delete_operation_callee)
        if user_utils.is_forbidden_user_model_operation(delete_operation):
            raise PermissionDenied

        user_to_be_deleted.is_active = False # Deactivate the user
        user_to_be_deleted.save()
        deleted_user = user_to_be_deleted
        
        deleted_user_full_name = "%s %s" %(deleted_user.first_name, deleted_user.last_name)
        messages.success(self.request, "User: %s deleted successfully" %(deleted_user_full_name))

        return HttpResponseRedirect(reverse("list_users"))
    

class ResetPassword(View):

    def get(self, *args, **kwargs):
        reset_password_form = user_forms.ResetPasswordForm()
        return render(self.request, "user/reset_password.html.development", {"form": reset_password_form})


    def post(self, *args, **kwargs):
        reset_password_form = user_forms.ResetPasswordForm(self.request.POST)
        email_template = "user/reset_password_email.txt.development"
        
        if reset_password_form.is_valid():
            user_id = kwargs.get("pk")
            email_subject = "Password Reset"
            phone_no = reset_password_form.cleaned_data.get("phone_no")
            from_email = "harmless_me@protonmail.com"
            user = User.objects.get(phone_no=phone_no)
            if user and user.email:
                to_email = user.email
                context = self.get_context_data(user)
                message = render_to_string(email_template, context)
                send_mail(email_subject, message, from_email, [to_email], html_message=message)
                
            # Donot alert the user about users that donot exist
            messages.success(self.request, "Email with password reset instructions has been sent. Please make sure you check your spam folder if you don't see the email.")
            return render(self.request, "user/reset_password.html.development", {"form": reset_password_form})

    def get_context_data(self, user):
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        email = user.email
        first_name = user.first_name
    
        # Context for the reset password sms 
        context = {
            "site_name": "Leigt Systems",
            "protocol": settings.PROTOCOL,
            "domain": settings.HOST,
            "uid": uidb64,
            "token": token,
            "email": email,
            "first_name": first_name,
            "browser_name": "%s %s" %(self.request.user_agent.browser.family, self.request.user_agent.browser.version_string),
            "operating_system": "%s %s" %(self.request.user_agent.os.family, self.request.user_agent.os.version_string),
        }
        return context

    
    
@login_required
def dashboard(request):
    return render(request, "user/dashboard.html.development")


@login_required
def profile(request):
    user = request.user
    edit_user_profile_form = user_forms.EditUserProfileForm(user=user)
    change_password_form = user_forms.ChangePasswordForm(user=user)
    context = {
        "edit_user_profile_form": edit_user_profile_form,
        "change_password_form": change_password_form,
    }
    return render(request, "user/profile.html.development", context)
