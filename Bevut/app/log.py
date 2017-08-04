from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.models import LogEntry, CHANGE, ADDITION, DELETION


CHA = CHANGE
ADD = ADDITION
DEL = DELETION


def log(msg, user, instance, action=CHA):
    content_type = ContentType.objects.get_for_model(instance)
    LogEntry.objects.log_action(user.pk, content_type.pk, instance.pk, repr(instance), action, msg)

# vi: ts=4 expandtab
