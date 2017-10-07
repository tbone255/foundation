# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.encoding import force_text
from django.utils.http import urlencode
from django.utils.translation import ugettext

from ...controller import MultipleObjectMixin
from ..controller import IS_POPUP_VAR, TO_FIELD_VAR, ERROR_FLAG, SEARCH_VAR
from .base import ControllerViewMixin
from .mixins import PaginationMixin, SearchMixin

__all__ = 'ListMixin',


class ListMixin(PaginationMixin, SearchMixin, MultipleObjectMixin,
                ControllerViewMixin):

    mode = 'list'

    def handle_common(self, handler, request, *args, **kwargs):

        # store the query string and prune it as we go
        self.params = dict(request.GET.items())
        self.is_popup = IS_POPUP_VAR in request.GET
        to_field = request.GET.get(TO_FIELD_VAR)
        if to_field and not model_admin.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField("The field %s cannot be referenced." % to_field)
        self.to_field = to_field

        if ERROR_FLAG in self.params:
            del self.params[ERROR_FLAG]

        if self.is_popup:
            self.list_editable = ()
        self.query = request.GET.get(SEARCH_VAR, '')

        # Get search parameters from the query string.
        self.get_results(view)
        if self.is_popup:
            title = ugettext('Select %s')
        else:
            title = ugettext('Select %s to change')
        self.title = title % force_text(self.opts.verbose_name)
        self.pk_attname = self.lookup_opts.pk.attname

        return super(ListMixin, self).handle_common(handler, request, *args, **kwargs)

    def get_query_string(self, new_params=None, remove=None):
        """ QueryString to pass back with response. """
        if new_params is None:
            new_params = {}
        if remove is None:
            remove = []
        p = self.params.copy()
        for r in remove:
            for k in list(p):
                if k.startswith(r):
                    del p[k]
        for k, v in new_params.items():
            if v is None:
                if k in p:
                    del p[k]
            else:
                p[k] = v
        return '?%s' % urlencode(sorted(p.items()))
