# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .. import backend
from .views.base import RESTChild, RESTParent
from .viewsets import RESTViewSet
from django.utils.functional import cached_property

__all__ = 'RESTController', 'RESTInline'


class RESTOptions(backend.controllers.PartialViewOptions):

    readonly_fields = ()

    classes = None


class RESTController(RESTOptions, backend.Controller):
    """
    Convenience Controller with PageViewSet attached to default namespace.
    """

    view_child_class = RESTChild
    view_parent_class = RESTParent
    viewsets = {
        None: RESTViewSet,
    }


class RESTInline(RESTOptions, RESTChild):

    @cached_property
    def parent_model(self):
        return self.view.controller.model

    def __getattribute__(self, name):
        """
        When a normal lookup fails, perform a secondary lookup in the model.
        """
        super_getattr = super(RESTInline, self).__getattribute__

        try:
            return super_getattr(name)
        except AttributeError as e:
            model = super_getattr('model')
            try:
                return getattr(model._meta, name)
            except AttributeError:
                raise e
