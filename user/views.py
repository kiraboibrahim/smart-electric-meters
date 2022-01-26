from django.shortcuts import render, get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Q
from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin
from user.forms import SuperAdminCreateUserForm, EditUserForm, AdminCreateUserForm, RevokePasswordForm
from user.acc_types import SUPER_ADMIN, ADMIN, MANAGER
# Create your views here.

User = get_user_model()

@user_passes_test(is_admin_or_super_admin)
def list_users(request):
    user_type = SUPER_ADMIN or request.user.acc_type
    users = None
    if user_type == SUPER_ADMIN:
        # List admin and  manger accounts
        users = User.objects.filter(Q(acc_type=MANAGER) | Q(acc_type=ADMIN))
        
    elif user_type == ADMIN:
        # List only manager accounts
        users = User.objects.filter(Q(acc_type=MANAGER))
        
    return render(request, "user/list_accounts.html.development", {"users": users})
    

@user_passes_test(is_admin_or_super_admin)
def edit_user(request, pk):
    # GET request
    user = get_object_or_404(User, pk=pk)
    if request.method == "POST":
        # process form and save updated fields
        edit_user_form = EditUserForm(request.POST, user=user)
        if edit_user_form.is_valid():
            edit_user_form.update() # Save the updated fields
            messages.success(request, "Changes saved successfully.")
        return render(request, "user/edit_user.html.development", {"form": edit_user_form})
    else:
        initial = {
            "first_name" : user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_no": user.phone_no,
            "address": user.address,
        }
        edit_user_form = EditUserForm(initial=initial)
        return render(request, "user/edit_user.html.development", {"form": edit_user_form}) 

@user_passes_test(is_admin_or_super_admin)
def create_user(request):
    user_type = request.user.acc_type
    designation = "Manager"
    if request.method == "POST":
        # Process the form and create user
        if user_type == SUPER_ADMIN:
            create_user_form = SuperAdminCreateUserForm(request.POST)
        elif user_type == ADMIN:
            create_user_form = AdminCreateUserForm(request.POST)

        if create_user_form.is_valid():
            user = create_user_form.save()
            if user.acc_type == ADMIN:
                designation = "Admin"
            # render the form with a success flash message attached
            messages.success(request, "%s: %s %s has been created successfully." %(designation, user.first_name, user.last_name))
            
        # Rerender the form 
        return render(request, 'user/create_user.html.development', {"form": create_user_form})

    else:
        # Render the AdminCreateUserForm or the SuperAdminCreateUserForm depending on the account type
        if user_type == SUPER_ADMIN:
            return render(request, 'user/create_user.html.development' ,{"form": SuperAdminCreateUserForm()})
        elif user_type == ADMIN:
            return render(request, 'user/create_user.html.development', {"form": AdminCreateUserForm()})

@login_required
def profile(request):
    return render(request, "user/profile.html.development")


@user_passes_test(is_admin_or_super_admin)
def revoke_password(request, pk):
    user = get_object_or_404(User, pk=pk)
    full_name = "%s %s" %(user.first_name, user.last_name)
    if request.method == "POST":
        form = RevokePasswordForm(request.POST, user=user)
        if form.is_valid():
            form.revoke_password()
        return render(request, "user/revoke_password.html.development", {"form": form, "full_name": full_name})
    else:
        form = RevokePasswordForm()
        return render(request, "user/revoke_password.html.development", {"form": form, "full_name": full_name})


def reset_password_request(request):
    pass
