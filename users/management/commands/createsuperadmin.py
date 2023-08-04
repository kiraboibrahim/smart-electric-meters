import getpass
import sys

from django.contrib.auth import get_user_model
from django.contrib.auth import password_validation
from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS
from django.forms import ValidationError
from django.utils.functional import cached_property
from django.utils.text import capfirst
from django.conf import settings

from phonenumber_field.phonenumber import PhoneNumber


PASSWORD_FIELD = "password"


class Command(BaseCommand):
    help = "Create a super administrator"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.UserModel = get_user_model()
        self.username_field = self.UserModel._meta.get_field(self.UserModel.USERNAME_FIELD)
        self.database = DEFAULT_DB_ALIAS

    def validate_username(self, username):
        if not username:
            return "Username cannot be blank"

        if self.username_is_unique:
            try:
                self.UserModel._default_manager.db_manager(self.database).get_by_natural_key(username)
            except self.UserModel.DoesNotExist:
                pass
            else:
                return "Error: %s is already taken" % username

        try:
            self.username_field.clean(username, None)
        except ValidationError as e:
            return "; ".join(e.messages)

    @cached_property
    def username_is_unique(self):
        if self.username_field.unique:
            return True
        return any(
            len(unique_constraint.fields) == 1 and unique_constraint.fields[0] == self.username_field.full_name
            for unique_constraint in self.UserModel._meta.total_unique_constraints
        )

    @staticmethod
    def get_field_prompt_message(field):
        return "%s%s: " % (
            capfirst(field.verbose_name),
            " (%s.%s)"
            % (
                field.remote_field.model._meta.object_name,
                field.m2m_target_field_name()
                if field.many_to_many
                else field.remote_field.field_name,
            )
            if field.remote_field
            else "",
        )

    def get_input_field_value(self, field):
        prompt_message = self.get_field_prompt_message(field)
        raw_value = input(prompt_message)
        try:
            val = field.clean(raw_value, None)
        except ValidationError as e:
            self.stderr.write("Error: %s" % "; ".join(e.messages))
            val = None
        return val

    def handle(self, *args, **options):
        user_data = {}
        # Has all required fields except for manytomany and foreign keys are represented as models and not raw IDs
        # Used for extensive password validation (Username similar to password validations)
        fake_user_data = {}
        username = None
        try:
            while username is None:
                username = PhoneNumber.from_string(self.get_input_field_value(self.username_field),
                                                   region=settings.PHONENUMBER_DEFAULT_REGION)
                error_msg = self.validate_username(username)
                if error_msg:
                    self.stderr.write(error_msg)
                    username = None
                    continue
            user_data[self.UserModel.USERNAME_FIELD] = username
            fake_user_data[self.UserModel.USERNAME_FIELD] = (
                self.username_field.remote_field.model(username)
                if self.username_field.remote_field
                else username
            )

            for field_name in self.UserModel.REQUIRED_FIELDS:
                field = self.UserModel._meta.get_field(field_name)
                user_data[field_name] = None
                while user_data[field_name] is None:
                    field_value = self.get_input_field_value(field)
                    user_data[field_name] = field_value
                    if field.many_to_many and field_value:
                        if not field_value.strip():
                            user_data[field_name] = None
                            self.stderr.write("Error: This field cannot be blank.")
                            continue
                        user_data[field_name] = [
                            pk.strip() for pk in field_value.split(",")
                        ]
                if not field.many_to_many:
                    fake_user_data[field_name] = user_data[field_name]

                # Wrap foreign keys into model instances
                if field.many_to_one:
                    fake_user_data[field_name] = field.remote_field.model(
                        user_data[field_name]
                    )

            user_data[PASSWORD_FIELD] = None
            while user_data[PASSWORD_FIELD] is None:
                password = getpass.getpass()
                password2 = getpass.getpass("Confirm password: ")
                if password != password2:
                    self.stderr.write("Password mismatch")
                    continue
                if password.strip() == "":
                    self.stderr.write("Blank passwords aren't allowed")
                    continue
                try:
                    password_validation.validate_password(password, self.UserModel(**fake_user_data))
                except ValidationError as error:
                    self.stderr.write("Password validation failed, please correct the following errors")
                    self.stderr.write("\n".join(error.messages))
                    continue
                else:
                    user_data[PASSWORD_FIELD] = password
            self.UserModel._default_manager.db_manager(self.database).create_super_admin(**user_data)
            self.stdout.write("Super administrator created successfully")

        except KeyboardInterrupt:
            self.stderr.write("\nOperation cancelled")
            sys.exit(1)

        except ValidationError as error:
            raise CommandError("\n".join(error.messages))
