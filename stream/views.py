from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from stream.models import Action


@login_required
def action_list(request):
    context = {'action_list': Action.objects.all()[:50]}
    return render(request, 'stream/action_list.html', context)
