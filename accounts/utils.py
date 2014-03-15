from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Group, Permission
from django.conf import settings


def get_admin_group():
    """
    Creates a group with the name from settings.AUTH_CODE_ADMIN_GROUP and adds
    all the permissions from the photos app.
    """
    group, created = Group.objects.get_or_create(
        name=settings.AUTH_CODE_ADMIN_GROUP)
    if created:
        content_types = ContentType.objects.filter(app_label='photos')
        new_perms = Permission.objects.filter(content_type__in=content_types)
        group.permissions = new_perms
        group.save()
    return group
