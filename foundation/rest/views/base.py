# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ...backend import views
from ...backend.views.controller.mixins import variables

IS_POPUP_VAR = '_popup'

IGNORED_PARAMS = variables.IGNORED_PARAMS + (IS_POPUP_VAR, )


class RESTChild(views.ViewChild):

    mode = 'LIST'


class RESTParent(views.ViewParent):

    pass


class RESTControllerMixin(views.ControllerViewMixin):

    def get_context_data(self, **kwargs):
        kwargs.update({
            'view_controller': self,
        })
        return super(RESTControllerMixin, self).get_context_data(**kwargs)
