# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import detail

from ...backend import views
from .base import RESTControllerMixin


__all__ = 'ObjectView',


class ObjectView(RESTControllerMixin, views.ObjectMixin, detail.DetailView):

    def get_success_url(self):
        return self.get_url('LIST')
