# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from ...controller.resolver import ModelResolver


class ChainingMixin(ModelResolver):
    """
    Provides ViewControllers with an ability to introspect and determine the URL
    for a particular mode given the current view and an optional, in-focus
    object.  This may be a View, ViewParent, or ViewChild (including inlines).
    """

    def get_url_kwargs(self, mode, **kwargs):
        url_name, url_kwargs = None, None


        # look for registered controller, bail if inline
        if not self.controller:
            return ValueError(
                'You attempted to use BaseController.get_url from an inline.  '
                'Refactor to use BaseViewController.get_url'
            )

        model_instance = None
        if obj is None:
            model_class = self.controller.model
        else:
            if issubclass(obj.__class__, models.Model):
                if isinstance(obj, models.Model):
                    model_class = obj.__class__
                    model_instance = obj
                else:
                    model_class = obj
                if self.controller.model != model_class:
                    
                    
            else:
                # if obj provided and not a model class or instance, bail
                raise ValueError('obj of type {} is not supported'.format(
                    type(obj)))

        # next determine if this is the controller of interest
        controller = self.controller
        url_model_class = 
        if not controller or controller.model != 


        # custom override for VIEW ONLY to handle special case of list/add
        url = None

        if not subcontroller and self.accessed_by_parent and mode in ('list', 'add'):
            # attempt to get mode as a parent subcontroller url
            url = self.parent.get_url(mode, self.controller, **kwargs)

        # normal lookup
        if not url:
            url = super(ControllerViewMixin, self).get_url(mode, subcontroller, **kwargs)

        return url




        url_name = self.get_url_name(mode, route=route)
        print(url_name)

            # if found, use the current single-object kwargs as the path
            #if url_name:
            #    url_kwargs = self.get_url_kwargs('view', **kwargs)

                # if a url is found there, look at the subcontroller to see if
                # if needs any additional help (e.g. the path)
                #url_kwargs = (
                #    subcontroller.get_url_kwargs(mode, **kwargs)
                ###    if subcontroller.is_local_root
                 ##   else self.get_url_kwargs('view', **kwargs)
                #)
        url_kwargs = self.get_url_kwargs(mode, **kwargs)

        return resolve_url(url_name, **url_kwargs) if url_name else None

    def get_url(self, mode, subcontroller=None, **kwargs):

        # custom override for VIEW ONLY to handle special case of list/add
        url = None

        if not subcontroller and self.accessed_by_parent and mode in ('list', 'add'):
            # attempt to get mode as a parent subcontroller url
            url = self.parent.get_url(mode, self.controller, **kwargs)

        # normal lookup
        if not url:
            url = super(ControllerViewMixin, self).get_url(mode, subcontroller, **kwargs)

        return url
