from django.shortcuts import render
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.forms import PasswordResetForm
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib import messages
from django.http import Http404, HttpResponse
from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin
from user.forms import SuperAdminCreateUserForm, EditUserForm, AdminCreateUserForm
from user.acc_types import SUPER_ADMIN, ADMIN, MANAGER
# Create your views here.

User = get_user_model()

@user_passes_test(is_admin_or_super_admin)
def list_users(request):
    user_type = request.user.acc_type
    if user_type == SUPER_ADMIN:
        # List admin manger accounts
        pass
    elif user_type == ADMIN:
        # List only manager accounts
        pass
    

@user_passes_test(is_admin_or_super_admin)
def edit_user(request, pk):
    if request.method == "POST":
        # process form and save updated fields
        edit_user_form = EdituserForm(request.POST)
        try:
            user = User.objects.get(id=pk)
        except:
            return Http404("Error occured")

        if edit_user_form.is_valid():
            pass
        
    # render form
    return render(request, "user/edit_user.html.development", {"form": EditUserForm()}) 

@user_passes_test(is_admin_or_super_admin)
def create_user(request):
    user_type = SUPER_ADMIN or request.user.acc_type
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
            messages.success(request, "%s: %s %s has been created successfully" %(designation, user.first_name, user.last_name))
            
        # Rerender the form 
        return render(request, 'user/create_user.html.development', {"form": create_user_form})

    else:
        # Render the AdminCreateForm or the SuperAdminCreateForm depending on the account type
        if user_type == SUPER_ADMIN:
            return render(request, 'user/create_user.html.development' ,{"form": SuperAdminCreateUserForm()})
        elif user_type == ADMIN:
            return render(request, 'user/creaet_user.html.development', {"form": AdminCreateUserForm()})

        

@user_passes_test(is_admin_or_super_admin)
def revoke_password(request, pk):
    pass


def reset_password_request(request):
    pass

@login_required
def profile(request):
    return render(request, "user/profile.html.development")
