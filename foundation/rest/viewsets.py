# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from rest_framework import mixins, viewsets

from ..backend import ControllerViewSet
from . import views
from django.utils.decorators import classonlymethod

__all__ = 'GenericViewSet', 'ReadOnlyModelViewSet', 'ModelViewSet'


class GenericViewSet(viewsets.GenericViewSet):

    controller = None

    @classonlymethod
    def as_view(cls, actions=None, **initkwargs):
        view = super(GenericViewSet, cls).as_view(actions=actions, **initkwargs)
        print(cls.controller, actions)
        # print(view.actions)
        # list {'get': 'list', 'post': 'create'}
        # detail {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        return view


class ReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           GenericViewSet):
    pass


class ModelViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericViewSet):
    pass


class OldRESTViewSet(ControllerViewSet):

    named_view_classes = (
        ('LIST', views.ListView),
        ('OBJECT', views.ObjectView),
    )

    def get_urlpatterns(self):
        model_lookup = self.router.controller.model_lookup
        urlpatterns = []

        # reserved modes list, add, and display need special treatment
        if 'LIST' in self:
            urlpatterns.append(url(r'^$', self['LIST'], name='LIST'))
        if 'OBJECT' in self:
            urlpatterns.append(url(
                r'^(?P<{lookup}>[-\w]+)$'.format(lookup=model_lookup),
                self['OBJECT'],
                name='OBJECT',
            ))

        return urlpatterns
