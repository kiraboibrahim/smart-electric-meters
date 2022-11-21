from django.shortcuts import render, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.conf import settings
from django.template.loader import render_to_string
from django.core.exceptions import PermissionDenied
from django.views.generic.list import ListView
from django.views.generic.edit import UpdateView, FormMixin, CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import View
from django.core.mail import send_mail

from search_views.filters import build_q

from prepaid_meters_token_generator_system.forms import SearchForm
from prepaid_meters_token_generator_system.auth.mixins import AdminOrSuperAdminRequiredMixin
from prepaid_meters_token_generator_system.views.mixins import SearchMixin

from user.forms import ResetPasswordForm, EditUserProfileForm, EditUserForm, ChangePasswordForm
from user.account_types import ADMIN, MANAGER
from user.utils import get_add_user_form_class, get_list_users_template_context_data, apply_user_filters, \
    is_forbidden_user_model_operation, ModelOperations
from user.models import UnitPrice
from user.filters import UserSearchFilter

User = get_user_model()


class BaseUserListView(ListView):
    template_name = "user/list_users.html.development"
    context_object_name = "users"
    model = User

    def get_queryset(self):
        users = apply_user_filters(self.request.user, super(BaseUserListView, self).get_queryset())
        return users

    def get_context_data(self, **kwargs):
        base_context = super(BaseUserListView, self).get_context_data(**kwargs)
        context = get_list_users_template_context_data(self.request, base_context)
        return context


class UserListView(AdminOrSuperAdminRequiredMixin, BaseUserListView):
    pass


class UserSearchView(BaseUserListView, SearchMixin):
    template_name = "user/search_users.html.development"
    http_method_names = ["get"]
    search_filters_class = UserSearchFilter

    def get_queryset(self):
        users = super(UserSearchView, self).get_queryset()
        search_filters = self.get_search_filters()
        return users.filter(search_filters)


class UserCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    template_name = "user/list_users.html.development"
    success_message = "%(designation)s: %(first_name)s %(last_name)s has been added successfully"
    http_method_names = ["post"]

    def post(self, *args, **kwargs):
        return super(UserCreateView, self).post(*args, **kwargs)

    def get_form_class(self):
        logged_in_user = self.request.user
        return get_add_user_form_class(logged_in_user)

    def get_success_message(self, cleaned_data):
        user_account_type = cleaned_data["account_type"]
        designation = "Manager"
        if user_account_type == ADMIN:
            designation = "Administrator"

        return self.success_message % dict(
            cleaned_data,
            designation=designation
        )

    def get_context_data(self, **kwargs):
        base_context = super(UserCreateView, self).get_context_data(**kwargs)
        context = get_list_users_template_context_data(self.request, base_context)
        return context

    def form_valid(self, form):
        self.object = form.save()
        user = self.object
        if user.account_type == MANAGER:
            # Only managers can a have unit price field
            unit_price = UnitPrice.objects.create(manager=user)
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UserEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    template_name = "user/edit_user.html.development"
    form_class = EditUserForm
    success_message = "Changes saved successfully"

    def get_success_url(self):
        return reverse_lazy("edit_user", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(UserEditView, self).get_context_data(**kwargs)
        logged_in_user = self.request.user
        context["users"] = apply_user_filters(logged_in_user, User.objects.all())
        return context

    def post(self, request, *args, **kwargs):
        user_being_edited = self.get_object()
        """
        Prevent admins from deleting fellow admins and super admins and likewise,
        prevent super admins from editing fellow super admins
        """
        edit_user_operation_caller = request.user
        edit_user_operation_callee = user_being_edited
        operation_type = ModelOperations.EDIT
        edit_operation = (operation_type, edit_user_operation_caller, edit_user_operation_callee)

        if is_forbidden_user_model_operation(edit_operation):
            raise PermissionDenied

        return super(UserEditView, self).post(request, *args, **kwargs)


class UserProfileEditView(LoginRequiredMixin, View):
    template_name = "user/profile.html.development"

    def get(self, *args, **kwargs):
        return HttpResponseRedirect(reverse("profile"))

    def post(self, *args, **kwargs):
        return self.update_user_personal_info(self.request.user)

    def update_user_personal_info(self, user):
        success_message = "Changes saved successfully"
        edit_user_profile_form = EditUserProfileForm(self.request.POST, instance=user)

        if edit_user_profile_form.is_valid():
            edit_user_profile_form.save()
            messages.success(self.request, success_message)

        context = self.get_context_data(edit_user_profile_form=edit_user_profile_form)
        return render(self.request, self.template_name, context=context)

    def get_context_data(self, **kwargs):
        context = {
            "change_password_form": ChangePasswordForm(user=self.request.user)
        }
        context.update(kwargs)
        return context


class ChangePasswordView(LoginRequiredMixin, View):
    template_name = "user/profile.html.development"
    http_method_names = ["post"]

    def post(self, request, *args, **kwargs):
        success_message = "Password changed successfully"
        change_password_form = ChangePasswordForm(request.POST, user=request.user)
        if change_password_form.is_valid():
            change_password_form.change_password()
            messages.success(request, success_message)

        context = self.get_context_data(change_password_form=change_password_form)
        return render(request, self.template_name, context=context)

    def get_context_data(self, **kwargs):
        context = {
            "edit_user_profile_form": EditUserProfileForm(user=self.request.user)
        }
        context.update(kwargs)
        return context


class UserDeleteView(AdminOrSuperAdminRequiredMixin, View):

    def get(self, *args, **kwargs):
        pk = kwargs.get("pk")
        user_to_be_deleted = get_object_or_404(User, pk=pk)

        delete_operation_caller = self.request.user
        delete_operation_callee = user_to_be_deleted
        operation_type = ModelOperations.DELETE
        delete_operation = (operation_type, delete_operation_caller, delete_operation_callee)
        if is_forbidden_user_model_operation(delete_operation):
            raise PermissionDenied

        user_to_be_deleted.is_active = False  # Deactivate the user
        user_to_be_deleted.save()
        deleted_user = user_to_be_deleted

        deleted_user_full_name = "%s %s" % (deleted_user.first_name, deleted_user.last_name)
        messages.success(self.request, "User: %s deleted successfully" % deleted_user_full_name)

        return HttpResponseRedirect(reverse("list_users"))


class UnitPriceEditView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnitPrice
    fields = "__all__"
    template_name = "user/register_price_per_unit.html.development"
    success_message = "Changes saved successfully"
    success_url = reverse_lazy("list_users")


class ResetPassword(View):
    def get(self, *args, **kwargs):
        reset_password_form = ResetPasswordForm()
        return render(self.request, "user/reset_password.html.development", {"form": reset_password_form})

    def post(self, *args, **kwargs):
        reset_password_form = ResetPasswordForm(self.request.POST)
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

            # Do not alert the user about users that do not exist
            messages.success(self.request, "Email with password reset instructions has been sent. "
                                           "Please make sure you check your spam folder if you don't see the email.")
            return render(self.request, "user/reset_password.html.development", {"form": reset_password_form})

    def get_context_data(self, user):
        token = default_token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        email = user.email
        first_name = user.first_name

        # Context for the reset password sms 
        context = {
            "site_name": "Legit Systems",
            "protocol": settings.PROTOCOL,
            "domain": settings.HOST,
            "uid": uidb64,
            "token": token,
            "email": email,
            "first_name": first_name,
            "browser_name": "%s %s" % (self.request.user_agent.browser.family,
                                       self.request.user_agent.browser.version_string),
            "operating_system": "%s %s" % (
                self.request.user_agent.os.family, self.request.user_agent.os.version_string),
        }
        return context


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
