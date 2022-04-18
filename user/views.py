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
from meter.utils import is_admin, is_super_admin, is_admin_or_super_admin
from meter.api import SMS
from user.forms import SuperAdminCreateUserForm, EditUserForm, AdminCreateUserForm, RevokePasswordForm, ResetPasswordForm
from user.acc_types import SUPER_ADMIN, ADMIN, MANAGER
from user.utils import allow_or_deny_action
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
        users = User.objects.filter(Q(acc_type=MANAGER) | Q(acc_type=ADMIN))
        
    return render(request, "user/list_accounts.html.development", {"users": users})
    

@user_passes_test(is_admin_or_super_admin)
def edit_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    # Prevent admins from deleting fellow admins and super admins and likewise prevent super admins from editing fellow super admins
    allow_or_deny_action(request.user.acc_type, user)
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
    designation = "Manager" # A designation that will used in the flash messages when a user is created; by de
    # default I have set it to manager

    if request.method == "POST":
        # Admins can only create manger accounts and super admins can create admins and managers
        # Thats the reason for two different forms
        if user_type == SUPER_ADMIN:
            create_user_form = SuperAdminCreateUserForm(request.POST)
        elif user_type == ADMIN:
            create_user_form = AdminCreateUserForm(request.POST)

        if create_user_form.is_valid():
            user = create_user_form.save()
            if user.acc_type == ADMIN:
                designation = "Admin" # The account created is for an admin, change the designation
                
            # render the form with a success flash message attached
            messages.success(request, "%s: %s %s has been created successfully." %(designation, user.first_name, user.last_name))
            
        # Rerender the form and display any errors if any 
        return render(request, 'user/create_user.html.development', {"form": create_user_form})

    else:
        # This is a GET request
        # Render the AdminCreateUserForm or the SuperAdminCreateUserForm depending on the account type of the logged in user
        if user_type == SUPER_ADMIN:
            return render(request, 'user/create_user.html.development' ,{"form": SuperAdminCreateUserForm()})
        elif user_type == ADMIN:
            return render(request, 'user/create_user.html.development', {"form": AdminCreateUserForm()})


@user_passes_test(is_admin_or_super_admin)
def revoke_password(request, pk):
    """ Revoking a password doesnot require an active session and it is specifically limitted to  admins and super admins 
    
    """
    user = get_object_or_404(User, pk=pk)
    # Donot allow admins to revoke super admin and fellow admin accounts passwords and likewise stop super admins from revoking
    # passwords of fellow super admins
    allow_or_deny_action(request.user.acc_type, user)
    # This will be used to give an informative message of what account has been deleted
    full_name = "%s %s" %(user.first_name, user.last_name)
    if request.method == "POST":
        form = RevokePasswordForm(request.POST, user=user)
        if form.is_valid():
            form.revoke_password()
        return render(request, "user/revoke_password.html.development", {"form": form, "full_name": full_name})
    else:
        form = RevokePasswordForm()
        return render(request, "user/revoke_password.html.development", {"form": form, "full_name": full_name})


@user_passes_test(is_admin_or_super_admin)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    # Prevent admins from deleting super admin and fellow admin accounts and likewise super admins from deleting fellow super admin accounts
    allow_or_deny_action(request.user.acc_type, user)
    # Delete user 
    user.delete()
    full_name = "%s %s" %(user.first_name, user.last_name)
    messages.success(request, "User: %s deleted successfully" %(full_name))
    return HttpResponseRedirect(request.META.get("HTTP_REFERER"))

def reset_password(request):
    if request.method == "POST":
        form = ResetPasswordForm(request.POST)
        user = None
        
        if form.is_valid():
            phone_no = form.cleaned_data["phone_no"]
            try:
                user = User.objects.get(phone_no=phone_no)
            except:
                pass
            
            if user is not None:
                token = default_token_generator.make_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))

                c = {
                    "site_name": "LEGIT SYSTEMS",
                    "protocol": "http",
                    "domain": "localhost:8000",
                    "uid": uidb64,
                    "token": token,
                }
                message_body = render_to_string("user/reset_password_sms.txt.development", c)
               
                # send the SMS with the password reset link

                sms_client = SMS(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN, settings.TWILIO_PHONE_NO)
                phone_no = "%s%s" %("+256", phone_no[1:])
                sms_client.send(phone_no, message_body)
            messages.success(request, "SMS with password reset instructions has been sent.")
            return render(request, "user/reset_password.html.development", {"form": form})

    else:
        form = ResetPasswordForm()
        return render(request, "user/reset_password.html.development", {"form": form})


@login_required
def profile(request):
    return render(request, "user/profile.html.development")
