from django.contrib.contenttypes.fields import GenericRelation
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.conf import settings
from django.utils import timezone
from django.db import models


class Action(models.Model):
    """
    An action is something that a user did.
    Nomenclature mostly based on http://activitystrea.ms/specs/atom/1.0/

    Generalized Format:
        <user> <verb>
        <user> <verb> <target>
        <user> <verb> <action_object> <target>
        <user> <verb> <action_object> <join> <target>

    Examples:
        <tim> <added new photos>
        <tim> <added 5 photos to the album> <Album Name>
        <tim> <tagged> <Photo Name> <Album Name>
        <tim> <tagged> <john> <in the album> <Album Name>
    """

    timestamp = models.DateTimeField(_('timestamp'), default=timezone.now)
    verb = models.CharField(_('verb'), max_length=200)
    join = models.CharField(_('join'), max_length=50, null=True, blank=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_('user'))

    target_content_type = models.ForeignKey(ContentType, related_name='target',
                                            blank=True, null=True)
    target_object_id = models.CharField(max_length=200, blank=True, null=True)
    target = generic.GenericForeignKey('target_content_type',
                                       'target_object_id')

    action_object_content_type = models.ForeignKey(
        ContentType, related_name='action_object', blank=True, null=True)
    action_object_object_id = models.CharField(
        max_length=200, blank=True, null=True)
    action_object = generic.GenericForeignKey('action_object_content_type',
                                              'action_object_object_id')

    class Meta:
        verbose_name = _('action')
        verbose_name_plural = _('actions')
        ordering = ['-timestamp', ]

    def __str__(self):
        ctx = {
            'actor': self.user.get_full_name() or self.user.username,
            'verb': self.verb,
            'join': self.join,
            'action_object': self.action_object,
            'target': self.target
        }
        if self.target:
            if self.action_object:
                return _('%(actor)s %(verb)s %(action_object)s %(join)s \
                    %(target)s') % ctx
            return _('%(actor)s %(verb)s %(target)s') % ctx
        if self.action_object:
            return _('%(actor)s %(verb)s %(action_object)s') % ctx
        return _('%(actor)s %(verb)s') % ctx


class ActionableModel(models.Model):
    """
    We define this model so that any class that should show up in the stream
    can subclass it. That way, if the object is deleted, any subsequent Action
    objects will also be deleted. If you don't use this as the base class,
    the associated Action will not be deleted whenever the associated model
    instance is deleted.
    """

    stream_action_objects = GenericRelation(
        Action,
        content_type_field='action_object_content_type',
        object_id_field='action_object_object_id')
    stream_action_targets = GenericRelation(
        Action,
        content_type_field='target_content_type',
        object_id_field='target_object_id')

    class Meta:
        abstract = True
