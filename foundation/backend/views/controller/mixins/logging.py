# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.utils.translation import override as translation_override

from ....utils import get_content_type_for_model

__all__ = 'LoggingMixin',


class LoggingMixin(object):
    """ NOT YET INTEGRATED """

    @translation_override(None)
    def construct_change_message(self, request, form, formsets, add=False):
        """
        Construct a JSON structure describing changes from a changed object.
        Translations are deactivated so that strings are stored untranslated.
        Translation happens later on LogEntry access.
        """
        change_message = []
        if add:
            change_message.append({'added': {}})
        elif form.changed_data:
            change_message.append({'changed': {'fields': form.changed_data}})

        if formsets:
            for formset in formsets:
                for added_object in formset.new_objects:
                    change_message.append({
                        'added': {
                            'name': force_text(added_object._meta.verbose_name),
                            'object': force_text(added_object),
                        }
                    })
                for changed_object, changed_fields in formset.changed_objects:
                    change_message.append({
                        'changed': {
                            'name': force_text(changed_object._meta.verbose_name),
                            'object': force_text(changed_object),
                            'fields': changed_fields,
                        }
                    })
                for deleted_object in formset.deleted_objects:
                    change_message.append({
                        'deleted': {
                            'name': force_text(deleted_object._meta.verbose_name),
                            'object': force_text(deleted_object),
                        }
                    })
        return change_message

    def log_addition(self, request, object, message):
        """
        Log that an object has been successfully added.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, ADDITION
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=ADDITION,
            change_message=message,
        )

    def log_change(self, request, object, message):
        """
        Log that an object has been successfully changed.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, CHANGE
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=force_text(object),
            action_flag=CHANGE,
            change_message=message,
        )

    def log_deletion(self, request, object, object_repr):
        """
        Log that an object will be deleted. Note that this method must be
        called before the deletion.

        The default implementation creates an admin LogEntry object.
        """
        from django.contrib.admin.models import LogEntry, DELETION
        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=get_content_type_for_model(object).pk,
            object_id=object.pk,
            object_repr=object_repr,
            action_flag=DELETION,
        )
