from django.utils.translation import ugettext as _
from django.shortcuts import redirect, render
from django.conf import settings
from django.contrib import messages
from django.http import Http404
from django.core.urlresolvers import reverse
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import login as login_view, logout_then_login

from accounts.forms import ProfileForm, RegisterForm, AuthenticationForm, \
    PasswordResetForm, SetPasswordForm, PasswordChangeForm


User = get_user_model()


def login(request):
    return login_view(request, template_name='accounts/login.html',
                      authentication_form=AuthenticationForm)


def logout(request):
    return logout_then_login(request)


def register(request, auth=None):
    initial = {'auth_code': auth}
    form = RegisterForm(request.POST or None, initial=initial)
    if form.is_valid():
        form.save()
        messages.success(request,
                         _('Your account has been created. \
                         You may now log in.'))
        return redirect(reverse('accounts:login'))
    context = {'form': form}
    return render(request, 'accounts/register.html', context)


@login_required()
def profile(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request,
                         _('Your profile has been updated.'))
        return redirect(reverse('accounts:profile'))
    context = {'form': form}
    return render(request, 'accounts/profile.html', context)


def password_reset(request):
    form = PasswordResetForm(request.POST or None)
    if form.is_valid():
        opts = {
            'use_https': request.is_secure(),
            'token_generator': default_token_generator,
            'from_email': settings.DEFAULT_FROM_EMAIL,
            'email_template_name': 'accounts/password_reset_email.html',
            'subject_template_name': 'accounts/password_reset_subject.txt',
            'request': request
        }
        form.save(**opts)
        messages.success(request,
                         _('You will receive an email with instructions to \
                         reset your password. Please look for it.'))
        return redirect(reverse('accounts:login'))
    context = {'form': form}
    return render(request, 'accounts/password_reset.html', context)


def password_reset_confirm(request, uidb64, token):
    # Check to make sure the user exists based on the token.
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        raise Http404(
            'Invalid token provided. uidb64=%s token=%s' % (uidb64, token))
    # And then check the token to make sure it belongs to the user.
    if not default_token_generator.check_token(user, token):
        raise Http404(
            'Invalid token provided. uidb64=%s token=%s' % (uidb64, token))
    # Then if everything is good we can process as normal.
    form = SetPasswordForm(request.POST or None, instance=user)
    if form.is_valid():
        form.save()
        messages.success(request,
                         _('Your password has been successfully changed. \
                         You may now log in.'))
        return redirect(reverse('accounts:login'))
    context = {'uidb64': uidb64, 'token': token, 'form': form}
    return render(request, 'accounts/password_reset_confirm.html', context)


@login_required()
def password_change(request):
    form = PasswordChangeForm(request.POST or None, instance=request.user)
    if form.is_valid():
        form.save()
        messages.success(request,
                         _('Your password has been successfully changed.'))
        return redirect(reverse('accounts:password_change'))
    context = {'form': form}
    return render(request, 'accounts/password_change.html', context)
