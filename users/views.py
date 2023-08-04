from django.conf import settings
from django.urls import reverse
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic.base import TemplateView

from django.views.generic.edit import UpdateView, CreateView, FormView

from django_filters.views import FilterView

from meter_vendors.models import MeterVendor
from meters.models import Meter
from recharge_tokens.models import RechargeTokenOrder

from .forms import (
    PasswordResetForm,
    MyProfileUpdateForm,
    UserUpdateForm,
    PasswordChangeForm,
    UnitPriceUpdateForm,
    ManagerCreateForm,
    AdminCreateForm,
    SetPasswordForm
)
from .filters import UserFilter
from .mixins import AdminOrSuperAdminRequiredMixin, ManagerRequiredMixin
from .models import UnitPrice
from .decorators import provide_user_list_template_context
from .account_types import ADMIN, MANAGER

User = get_user_model()


class MyDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "users/dashboard.html"

    def get_context_data(self, **kwargs):
        context = {
            'order_count': RechargeTokenOrder.objects.all().for_user(self.request.user).count(),
            'meter_count': Meter.objects.all().for_user(self.request.user).count()
        }
        if self.request.user.is_admin() or self.request.user.is_super_admin():
            context["user_count"] = User.objects.all().for_user(self.request.user).count()
            context["vendor_count"] = MeterVendor.objects.all().count()
        return context


class MyProfileView(LoginRequiredMixin, TemplateView):
    template_name = "users/profile.html"

    def get_context_data(self, **kwargs):
        context = {
            "my_profile_update_form": MyProfileUpdateForm(self.request.user),
            "password_change_form": PasswordChangeForm(self.request.user),
            "unit_price_update_form": UnitPriceUpdateForm(self.request.user)
        }
        return context


@provide_user_list_template_context
class UserListView(LoginRequiredMixin, FilterView):
    template_name = "users/user_list.html"
    context_object_name = "users"
    model = User
    paginate_by = settings.LEGIT_SYSTEMS_MAX_ITEMS_PER_PAGE
    filterset_class = UserFilter


@provide_user_list_template_context
class UserCreateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, CreateView):
    model = User
    fields = ["first_name", "last_name", "email", "phone_no", "address"]
    template_name = "users/user_list.html"
    success_message = "User has been added"
    success_url = reverse_lazy("user_list")
    http_method_names = ["post"]

    def get_form_class(self):
        account_type = int(self.request.GET.get("type", MANAGER))
        if account_type not in (ADMIN, MANAGER):
            raise Http404
        return AdminCreateForm if account_type == ADMIN else ManagerCreateForm

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        self.object = form.save()
        messages.success(self.request, self.get_success_message(form.cleaned_data))
        return redirect(self.success_url)

    def form_invalid(self, form):
        form_context_name = "admin_create_form" if isinstance(form, AdminCreateForm) else "manager_create_form"
        return self.render_to_response(self.get_context_data(**{f'{form_context_name}': form}))


@provide_user_list_template_context
class UserUpdateView(AdminOrSuperAdminRequiredMixin, SuccessMessageMixin, UpdateView):
    """Change user's password or biography"""

    model = User
    template_name = "users/user_list.html"
    success_url = reverse_lazy("user_list")
    success_message = "Changes have been saved"

    def get_form_class(self):
        scope = self.request.GET.get("scope", "bio")
        if scope not in ("bio", "pwd"):
            raise Http404
        if scope == "pwd":
            return SetPasswordForm
        return UserUpdateForm

    def get_form(self, form_class=None):
        form_class = self.get_form_class()
        if issubclass(form_class, SetPasswordForm):
            kwargs = self.get_form_kwargs()
            kwargs.pop("instance")  # SetPasswordForm isn't a model form and thus, it doesn't expect instance arg
            kwargs.pop("initial")  # SetPasswordForm doesn't need initial data
            return form_class(self.object, **kwargs)
        return form_class(self.request.user, **self.get_form_kwargs())  # User wants to update regular fields

    def get_initial(self):
        return {
                "first_name": self.object.first_name,
                "last_name": self.object.last_name,
                "email": self.object.email,
                "address": self.object.address,
                "phone_no": self.object.phone_no,
                "account_type": self.object.account_type
        }

    def form_invalid(self, form):
        context = self.get_context_data(form=form)
        if isinstance(form, SetPasswordForm):  # SetPassword Form has been submitted
            context["set_password_form"] = form
            context["user_update_form"] = UserUpdateForm(self.request.user, initial=self.get_initial())  # Initialize
            # UserUpdateForm with user data because it isn't the form that is submitted, and we wouldn't want it to
            # be empty
        else:
            context["user_update_form"] = form
        return self.render_to_response(context=context)


class MyProfileUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    form_class = MyProfileUpdateForm
    template_name = "users/profile.html"
    success_message = "Changes have been saved"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(reverse("profile"))

    def get_form(self, form_class=None):
        form_class = super().get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def form_invalid(self, form):
        return self.render_to_response(context=self.get_context_data(my_profile_update_form=form, password_change_form=PasswordChangeForm(self.request.user)))


class MyPasswordChangeView(LoginRequiredMixin, SuccessMessageMixin, FormView):
    form_class = PasswordChangeForm
    template_name = "users/profile.html"
    http_method_names = ["post"]
    success_message = "Password has been changed"

    def get_form(self, form_class=None):
        form_class = super().get_form_class()
        return form_class(self.request.user, **self.get_form_kwargs())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["my_profile_update_form"] = MyProfileUpdateForm(self.request.user)
        context["password_change_form"] = context["form"]
        return context


class UserDeleteView(AdminOrSuperAdminRequiredMixin, UserPassesTestMixin, SuccessMessageMixin, View):
    to_be_deleted_user = None
    error_message = "User: %(full_name)s can't be deleted. There are still meters associated to this users"
    success_message = "User: %(full_name)s has been deleted"

    def test_func(self):
        self.to_be_deleted_user = get_object_or_404(User, pk=self.kwargs.get("pk"))
        deleter = self.request.user
        if self.to_be_deleted_user.assert_same_account_type(deleter) or self.to_be_deleted_user.is_super_admin() or \
                self.to_be_deleted_user.is_default_manager():
            return False
        return True

    def get(self, *args, **kwargs):
        if not self.to_be_deleted_user.has_meters():
            self.to_be_deleted_user.delete()
            success_message = self.get_success_message({"full_name": self.to_be_deleted_user.full_name})
            messages.success(self.request, success_message)
        else:
            messages.error(
                self.request,
                self.error_message % ({"full_name": self.to_be_deleted_user.full_name})
            )
        return HttpResponseRedirect(reverse("user_list"))


class PasswordResetView(SuccessMessageMixin, FormView):
    form_class = PasswordResetForm
    template_name = "users/password_reset.html"
    success_message = "Email with password reset instructions has been sent " \
                      "Please make sure you check your spam folder if you don't see the email."

    def form_valid(self, form):
        form.save(request=self.request)
        messages.success(self.request, self.success_message)
        return self.render_to_response(context=self.get_context_data(form=form))

    def form_invalid(self, form):
        messages.success(self.request, self.success_message)
        return super().form_invalid(form)


class MyUnitPriceUpdateView(ManagerRequiredMixin, SuccessMessageMixin, UpdateView):
    model = UnitPrice
    fields = ["price"]
    success_message = "Unit price has been changed"
    success_url = reverse_lazy("profile")

    def get_object(self, queryset=None):
        return self.request.user.unitprice