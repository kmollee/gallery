from django.contrib import admin

from stream.models import Action


class ActionAdmin(admin.ModelAdmin):
    list_display = ['user', 'verb', 'target', 'timestamp']

admin.site.register(Action, ActionAdmin)
