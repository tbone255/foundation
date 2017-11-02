# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from ..backend import ControllerViewSet
from . import views

__all__ = 'APIViewSet',


class APIViewSet(ControllerViewSet):

    named_view_classes = (
        ('LIST', views.ControllerAPIView),
        ('object', views.ControllerAPIView),
    )

    def get_urlpatterns(self):
        model_lookup = self.router.controller.model_lookup
        urlpatterns = []

        # reserved modes list, add, and display need special treatment
        if 'LIST' in self:
            urlpatterns.append(url(r'^$', self['LIST'], name='LIST'))
        if 'object' in self:
            urlpatterns.append(url(
                r'^(?P<{lookup}>[-\w]+)$'.format(lookup=model_lookup),
                self['object'],
                name='object',
            ))

        return urlpatterns
