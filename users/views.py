from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.views import View
from django.views.generic.base import ContextMixin, TemplateResponseMixin
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView

from shared.auth.mixins import AdminOrSuperAdminRequiredMixin, ManagerRequiredMixin
from shared.forms import SearchForm as UserSearchForm
from shared.views import SearchListView
from manufacturers.models import MeterManufacturer
from meters.models import Meter
from recharge_tokens.models import RechargeToken
from .account_types import ADMIN, MANAGER
from .filters import UserSearchUrlQueryKwargMapping
from .forms import ResetPasswordForm, EditUserProfileForm, EditUserForm, ChangePasswordForm, ManagerUnitPriceEditForm, \
    CreateUserFormFactory
from .mixins import UsersContextMixin
from .models import UnitPrice
from .utils import get_users

User = get_user_model()


@login_required
def dashboard(request):
    template_name = "users/dashboard.html.development"
    context = {}
    all_meters = Meter.objects.all()
    all_recharge_tokens = RechargeToken.objects.all()
    if request.user.is_manager():
        context["meter_count"] = all_meters.filter(manager=request.user).count()
        context["recharge_token_count"] = all_recharge_tokens.filter(payment__user=request.user).count()
        template_name = "managers/users/dashboard.html.development"
    elif request.user.is_admin() or request.user.is_super_admin():
        all_meters = list(all_meters)
        all_manufacturers = MeterManufacturer.objects.all()
        context["meter_count"] = len(all_meters)
        context["inactive_meter_count"] = len(list(filter(lambda meter: meter.is_active != True, all_meters)))
        context["manufacturer_count"] = all_manufacturers.count()
        context["user_count"] = User.objects.all().count()
        context["recharge_token_count"] = all_recharge_tokens.count()
    return render(request, template_name, context=context)


@login_required
def profile(request):
    template_name = "users/profile.html.development"
    edit_user_profile_form = EditUserProfileForm(user=request.user)
    change_password_form = ChangePasswordForm(user=request.user)

    context = {
        "edit_user_profile_form": edit_user_profile_form,
        "change_password_form": change_password_form,
    }
    if request.user.is_manager():
        template_name = "managers/users/profile.html.development"
        context["unit_price_edit_form"] = ManagerUnitPriceEditForm(initial={'price': request.user.price_per_unit})

    return render(request, template_name, context)


class UserListView(AdminOrSuperAdminRequiredMixin, ListView):
    template_name = "users/list_users.html.development"
    context_object_name = "users"
    model = User
    extra_context = {
        "user_search_form": UserSearchForm()
    }
    paginate_by = settings.MAX_ITEMS_PER_PAGE

    def get_queryset(self):
        users = super().get_queryset()
        users = get_users(self.request.user, initial_users=users)
        return users

    def get_context_data(self, **kwargs):
        add_user_form = CreateUserFormFactory.get_form(self.request.user)
        context = super().get_context_data(**kwargs)
        context["add_user_form"] = add_user_form
        return context


class UserSearchView(SearchListView):
    model = User
    template_name = "users/list_users.html.development"
    http_method_names = ["get"]
    context_object_name = "users"
    extra_context = {
        "user_search_form": UserSearchForm()
    }
    paginate_by = settings.MAX_ITEMS_PER_PAGE
    search_url_query_kwarg_mapping_class = UserSearchUrlQueryKwargMapping

    def get_queryset(self):
        users = super().get_queryset()
        users = get_users(self.request.user, initial_users=users)
        return users

    def get_context_data(self, **kwargs):
        context = super(UserSearchView, self).get_context_data(**kwargs)
        context["user_search_form"] = UserSearchForm(self.request.GET)
        return context


class UserCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UsersContextMixin, CreateView):
    model = User
    template_name = "users/list_users.html.development"
    success_message = "%(designation)s: %(first_name)s %(last_name)s has been added"
    http_method_names = ["post"]
    extra_context = {
        "user_search_form": UserSearchForm(),
    }

    def post(self, *args, **kwargs):
        return super(UserCreateView, self).post(*args, **kwargs)

    def get_form_class(self):
        return CreateUserFormFactory.get_form(self.request.user).__class__

    def get_success_message(self, cleaned_data):
        account_type = cleaned_data["account_type"]
        designation = "Manager"
        if account_type == ADMIN:
            designation = "Administrator"

        return self.success_message % dict(
            cleaned_data,
            designation=designation
        )

    def get_context_data(self, **kwargs):
        users_context = self.get_users_context()
        context = super(UserCreateView, self).get_context_data(**kwargs)
        context["add_user_form"] = kwargs.pop("form")
        context.update(users_context)
        return context

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return self.render_to_response(self.get_context_data(form=form))

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class UserEditView(AdminOrSuperAdminRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, UpdateView):
    """
    This view manipulates both user personal information and password, The normal view flow works on personal
    information and the set_new_password() function updates the password.
    The information to edit depends on the scope GET parameter
    """

    model = User
    template_name = "users/edit_user.html.development"
    form_class = EditUserForm
    success_message = "Changes saved"

    def post(self, request, *args, **kwargs):
        scope = request.GET.get("scope", "personal-info")
        if scope == "personal-info":
            return super(UserEditView, self).post(request, *args, **kwargs)
        elif scope == "password":
            return self.set_new_password()

    def test_func(self):
        self.object = to_be_edited_user = self.get_object()
        editor = self.request.user
        if to_be_edited_user.assert_same_account_type(editor) or to_be_edited_user.is_super_admin() or \
                to_be_edited_user.is_default_manager():
            return False
        return True

    def set_new_password(self):
        set_password_form = SetPasswordForm(self.object, self.request.POST)
        if set_password_form.is_valid():
            set_password_form.save()
            messages.success(self.request, "Password updated")
            return HttpResponseRedirect(self.get_success_url())
        context = self.get_context_data(set_password_form=set_password_form,
                                        form=self.get_form_class()(instance=self.object))
        return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy("edit_user", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        context = super(UserEditView, self).get_context_data(**kwargs)
        # Set a proper name for generic form (user_personal_info_edit_form) to distinguish it from set_password_form
        context["user_personal_info_edit_form"] = context["form"]
        context["set_password_form"] = context["set_password_form"] if "set_password_form" in context else \
            SetPasswordForm(self.object)
        return context


class UserProfileEditView(LoginRequiredMixin, SuccessMessageMixin, ContextMixin, TemplateResponseMixin, View):
    template_name = "users/profile.html.development"
    success_message = "Changes saved"

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("profile"))

    def post(self, request, *args, **kwargs):
        return self.update_user_personal_info(request.user)

    def get_template_names(self):
        if self.request.user.is_manager():
            self.template_name = "managers/users/profile.html.development"
        return self.template_name

    def update_user_personal_info(self, user):
        edit_user_profile_form = EditUserProfileForm(self.request.POST, instance=user)

        if edit_user_profile_form.is_valid():
            edit_user_profile_form.save()
            messages.success(self.request, self.success_message)

        context = self.get_context_data(edit_user_profile_form=edit_user_profile_form)
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = {
            "change_password_form": ChangePasswordForm(user=self.request.user)
        }
        context.update(kwargs)
        return context


class ChangePasswordView(LoginRequiredMixin, SuccessMessageMixin, TemplateResponseMixin, View):
    template_name = "users/profile.html.development"
    http_method_names = ["post"]
    success_message = "Password changed successfully"

    def post(self, request, *args, **kwargs):
        change_password_form = ChangePasswordForm(request.POST, user=request.user)
        if change_password_form.is_valid():
            change_password_form.change_password()
            messages.success(request, self.success_message)

        context = self.get_context_data(change_password_form=change_password_form)
        return self.render_to_response(context=context)

    def get_context_data(self, **kwargs):
        context = {
            "edit_user_profile_form": EditUserProfileForm(user=self.request.user)
        }
        context.update(kwargs)
        return context


class UserDeleteView(AdminOrSuperAdminRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    to_be_deleted_user = None
    error_message = "User: %(full_name)s cannot be deleted. There are still meters associated to this manager"
    success_message = "User: %(full_name)s deleted"

    def test_func(self):
        user_id = self.kwargs.get("pk")
        self.to_be_deleted_user = get_object_or_404(User, pk=user_id)
        deleter = self.request.user
        if self.to_be_deleted_user.assert_same_account_type(deleter) or self.to_be_deleted_user.is_super_admin() or \
                self.to_be_deleted_user.is_default_manager():
            return False
        return True

    def get(self, *args, **kwargs):
        if not self.to_be_deleted_user.has_associated_meters():
            self.to_be_deleted_user.delete()
            success_message = self.get_success_message({"full_name": self.to_be_deleted_user.full_name})
            messages.success(self.request, success_message)
        else:
            messages.error(
                self.request,
                self.error_message % ({"full_name": self.to_be_deleted_user.full_name})
            )
        return HttpResponseRedirect(reverse("list_users"))


class UnitPriceEditView(ManagerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnitPrice
    fields = ["price"]
    success_message = "Unit price changed successfully"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user.unit_price


class ResetPassword(ContextMixin, SuccessMessageMixin, TemplateResponseMixin, View):
    template_name = "users/reset_password.html.development"
    success_message = "Email with password reset instructions has been sent " \
                      "Please make sure you check your spam folder if you don't see the email."

    password_reset_email_template_name = "users/reset_password_email.txt.development"
    email_subject = "Password Reset"
    from_email = "harmless_me@protonmail.com"
    user_to_reset = None

    def get(self, *args, **kwargs):
        reset_password_form = ResetPasswordForm()
        return self.render_to_response(context={"form": reset_password_form})

    def post(self, *args, **kwargs):
        reset_password_form = ResetPasswordForm(self.request.POST)
        if reset_password_form.is_valid():
            self.user_to_reset = reset_password_form.user
        self.send_password_reset_email()
        messages.success(self.request, self.success_message)
        return self.render_to_response(context={"form": reset_password_form})

    def send_password_reset_email(self):
        if self.user_to_reset and self.user_to_reset.email:
            email_message = self.get_email_message()
            send_mail(self.email_subject, email_message, self.from_email, [self.user_to_reset.email],
                      html_message=email_message)

    def get_email_message(self):
        password_reset_email_context = self.get_password_reset_email_context()
        email_message = render_to_string(self.password_reset_email_template_name, password_reset_email_context)
        return email_message

    def get_password_reset_email_context(self):
        reset_password_token = default_token_generator.make_token(self.user_to_reset)
        uid_b64 = urlsafe_base64_encode(force_bytes(self.user_to_reset.id))

        current_site = get_current_site(self.request)
        password_reset_email_context = {
            "site_name": current_site.name,
            "protocol": "https",
            "domain": current_site.domain,
            "uid": uid_b64,
            "token": reset_password_token,
            "email": self.user_to_reset.email,
            "first_name": self.user_to_reset.first_name,
            "browser_name": "%s %s" % (self.request.user_agent.browser.family,
                                       self.request.user_agent.browser.version_string),
            "operating_system": "%s %s" % (
                self.request.user_agent.os.family, self.request.user_agent.os.version_string),
        }
        return password_reset_email_context


class LoginAsManagerView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, SingleObjectMixin, View):
    success_message = "Logged in as: %(name)s"

    def get(self, request, *args, **kwargs):
        manager = self.get_object()
        logout(request)
        login(request, manager)
        messages.success(request, self.get_success_message({"name": manager.full_name}))
        return redirect(reverse("profile"))

    def get_queryset(self):
        return User.objects.filter(account_type=MANAGER)
