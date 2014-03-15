from stream.models import Action


def send_action(user, verb, action_object=None, join=None, target=None):
    """
    A shortcut method for creating an Action instance. This helps abstract out
    the actual Action model so other apps don't really need to know about its
    implementation.
    """
    action = Action.objects.create(
        user=user, verb=verb, action_object=action_object, join=join,
        target=target)
    return action
