from django.utils.translation import ugettext_lazy as _
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, \
    PasswordResetForm as BasePasswordResetForm, \
    SetPasswordForm as BaseSetPasswordForm, \
    PasswordChangeForm as BasePasswordChangeForm

from accounts.utils import get_admin_group


User = get_user_model()


class ProfileForm(forms.ModelForm):
    """
    User form that contains first name, last name, and email.
    """

    error_messages = {
        'duplicate_email': _('This email address is already in use. Please \
            supply a different email address.'),
    }

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        """
        Validates that the email address entered does not already exist in the
        database. We need to exclude the current email address otherwise
        this check will always fail.
        """
        email = self.cleaned_data['email']
        if User._default_manager.exclude(
                email=self.instance.email).filter(email=email):
            raise forms.ValidationError(self.error_messages['duplicate_email'])
        return email


class RegisterForm(UserCreationForm):
    """
    Form to create a user that includes first_name and last_name.
    Also includes an authorization code that must be entered correctly.
    """

    auth_code = forms.CharField(
        label=_('Authorization code'),
        help_text='Required. Enter the authorization code to create \
            your account.')
    email = forms.EmailField(
        help_text='Required. Used if you ever forget your password.')

    error_messages = dict(UserCreationForm.error_messages, **{
        'duplicate_email': _('This email address is already in use. Please \
            supply a different email address.'),
        'invalid_auth_code': _('Authorization code provided was not correct.'),
    })

    class Meta:
        model = User
        fields = ['auth_code', 'username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        """
        Validates that the email address entered does not already exist in the
        database.
        """
        email = self.cleaned_data['email']
        if User._default_manager.filter(email=email):
            raise forms.ValidationError(self.error_messages['duplicate_email'])
        return email

    def clean_auth_code(self):
        """
        Validates that the auth code is one of the two valid authorization
        codes so the user can create his account.
        """
        auth_code = self.cleaned_data['auth_code']
        if auth_code not in (settings.AUTH_CODE_USER,
                             settings.AUTH_CODE_ADMIN):
            raise forms.ValidationError(
                self.error_messages['invalid_auth_code'])
        return auth_code

    def clean_auth_code(self):
        """
        Validates that the auth code is one of the two valid authorization
        codes so the user can create his account. Sets self.is_admin_user so
        that the save method will know whether to create an admin account or
        a regular account.
        """
        auth_code = self.cleaned_data['auth_code']
        if auth_code == settings.AUTH_CODE_ADMIN:
            self.is_admin_user = True
            return auth_code
        if auth_code == settings.AUTH_CODE_USER:
            self.is_admin_user = False
            return auth_code
        raise forms.ValidationError(
            self.error_messages['invalid_auth_code'])

    def save(self, commit=True):
        """
        Saves the user and creates an admin account according to the variable
        self.is_admin_user.
        """
        user = super().save(commit=False)
        if commit:
            user.save()
        if self.is_admin_user:
            user.groups.add(get_admin_group())
        return user


class PasswordResetForm(BasePasswordResetForm):
    """
    Form to send an email to a user who has forgotten his password.
    """

    error_messages = {
        'invalid_email': _('A user with that email address could not be \
            found.'),
    }

    def clean_email(self):
        """
        Validates that the email address entered actually exists in
        the database.
        """
        email = self.cleaned_data['email']
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            raise forms.ValidationError(self.error_messages['invalid_email'])
        return email


class PasswordChangeForm(BasePasswordChangeForm):
    """
    Override the __init__ method on Django's PasswordChangeForm to make it
    more like a standard ModelForm.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs.pop('instance'), *args, **kwargs)


class SetPasswordForm(BaseSetPasswordForm):
    """
    Override the __init__ method on Django's SetPasswordForm to make it
    more like a standard ModelForm.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(kwargs.pop('instance'), *args, **kwargs)
