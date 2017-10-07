# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http.response import Http404
from django.utils.translation import ugettext as _

from ...controller import SingleObjectMixin
from .base import ControllerViewMixin

__all__ = 'ObjectMixin',


class ObjectMixin(SingleObjectMixin, ControllerViewMixin):

    mode = 'object'

    def get_object(self, queryset=None):
        """
        Returns the object the view is displaying.

        By default this requires `self.queryset` and a `pk` or `slug` argument
        in the URLconf, but subclasses can override this to return any object.
        """

        obj = super(ObjectMixin, self).get_object(queryset=queryset)

        # TODO: Consider if we want to support normal pk/slug stuff...

        if not obj:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': self.model._meta.verbose_name})
        return obj

    def add:

        if IS_POPUP_VAR in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR)

        elif "_continue" in request.POST or (
                # Redirecting after "Save as new".
                "_saveasnew" in request.POST and self.save_as_continue and
                self.has_change_permission(request, obj)
        ):

        elif "_addanother" in request.POST:

        else:


    def edit:

        if "_continue" in request.POST:

        elif "_saveasnew" in request.POST:

        elif "_addanother" in request.POST:

        else:

