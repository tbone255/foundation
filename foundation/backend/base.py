# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import logging

from collections import OrderedDict
from django.conf import settings
from django.conf.urls import url, include
from django.forms.widgets import MediaDefiningClass
from django.urls import resolve
from django.utils import six
from django.utils.functional import cached_property

from .. import utils
from .registry import NotRegistered, Registry
from foundation.backend.routers import PageRouter
from .views import TemplateView

__all__ = 'Backend', 'backends', 'get_backend'

logger = logging.getLogger(__name__)


class Backend(six.with_metaclass(MediaDefiningClass, Registry)):

    admin_site = None  # allows for alternate admin site to be provided
    admin_url_prefix = None  # '' to put on root, 'admin' to emulate normal
    auth_url_prefix = None  # '' to put on root, 'accounts' to emulate normal
    create_permissions = False
    routers = ()  # tuple of name-router_class tuples
    site_index_class = TemplateView
    site_index_name = 'index'
    _empty_value_display = '-'

    @property
    def site(self):
        """
        It may seem like this should need the request but the plan is to make
        a SiteBackend registry at some point... for now we will assume one site.
        """
        from django.contrib.sites.models import Site
        return Site.objects.get(pk=settings.SITE_ID)

    @property
    def site_title(self):
        return self.site.name

    def __init__(self, *args, **kwargs):
        '''
        self.name = name
        self._actions = {'delete_selected': actions.delete_selected}
        self._global_actions = self._actions.copy()
        '''
        self.backend = self
        self.named_routers = {}
        for name, router_class in self.routers:
            if name in self.named_routers:
                raise KeyError('APIRouter named "{}" already exists.'.foramt(name))
            self.named_routers[name] = router_class()
        if None not in self.named_routers:
            self.named_routers[None] = PageRouter()
        super(Backend, self).__init__(*args, **kwargs)

    def register(self, model_or_iterable, controller_class=None, **options):
        """
        Registers the given model(s) with the given controller class.

        The model(s) should be Model classes, not instances.

        If a controller class isn't given, it will use Controller (the default
        options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the controller class.

        If a model is already registered, this will raise AlreadyRegistered.

        If a model is abstract, this will raise ImproperlyConfigured.
        """
        from django.db.models.base import ModelBase
        if not controller_class:
            from .controllers import Controller
            controller_class = Controller
        if isinstance(model_or_iterable, ModelBase):
            model_or_iterable = [model_or_iterable]
        for model in model_or_iterable:
            super(Backend, self).register(controller_class, model, **options)

    def _populate_routers(self):

        # URL auto-loader traverses all project apps
        for app_config in utils.get_project_app_configs():

            app_namespace = getattr(app_config,
                                    'url_namespace',
                                    app_config.label)

            urlprefix = getattr(app_config, 'url_prefix', None)
            urlprefix = ((urlprefix or app_config.label)
                         if urlprefix != ''
                         else r'')

            # set backend on app_config since may be using django appconfigs and the
            # kwargs build-out for AppViewSets will look to AppConfig for backend
            app_config.backend = self

            # start by getting all controller urlpatterns in-depth
            for model in app_config.get_models():
                try:
                    controller = self.get_registered_controller(model)
                except NotRegistered:
                    continue

                controller_namespace = controller.model_namespace
                controller_prefix = controller.url_prefix

                # be nice and getattr to accommodate Django app_configs
                view_kwargs = dict(router=controller, app_config=app_config)
                for router_name, viewset in getattr(controller, 'viewsets', {}).items():
                    prefix = controller_prefix or urlprefix
                    viewset.controller = controller
                    viewset.queryset = controller.model.objects.all()
                    # viewset.queryset = controller.get_root_queryset()
                    print(router_name, viewset)
                    self.named_routers[router_name].register(prefix, viewset, base_name=None)

    @cached_property
    def urls(self):
        """
        Returns a complete list of URLs for this Backend.
        Can be used as a shortcut for attaching to ROOT_URLCONF
        """
        # register all viewsets to the appropriate routers
        self._populate_routers()
        urlpatterns = self.named_routers[None].urls
        urlpatterns.extend([
            url(r'^{}/'.format(router_name), include((router.urls, router_name)))
            for router_name, router in self.named_routers.items() if router_name != None
        ])
        return urlpatterns

    def get_available_apps(self, request):
        """
        Returns a sorted list of all the installed apps that have been
        registered in this site.
        """

        user = request.user
        available_apps = OrderedDict()
        for app_config in sorted(utils.get_project_app_configs(),
                                 key=lambda app_config: app_config.label):
            is_visible = False
            if app_config.has_public_views:
                is_visible = True
            elif user.has_module_perms(app_config.label):
                is_visible = True
            if is_visible:
                url_prefix = getattr(app_config, 'url_prefix', None)
                if url_prefix is None:
                    url_prefix = app_config.label
                try:
                    url = '/{}/'.format(url_prefix)
                    resolve(url)
                except:
                    pass
                else:
                    available_apps[app_config] = url

        return available_apps

    def each_context(self, request):
        """
        Returns a dictionary of variables to put in the template context for
        *every* page in the admin site.
        """

        return {
            'backend': self,
            'has_admin_urls': self.admin_site is not None,
            'has_auth_urls': self.auth_url_prefix is not None,
            'site_title': self.site_title,
            'available_apps': self.get_available_apps(request),
        }

    @property
    def empty_value_display(self):
        return self._empty_value_display

    @empty_value_display.setter
    def empty_value_display(self, empty_value_display):
        self._empty_value_display = empty_value_display


"""
Plan is to eventually actually allow for the declaration of per-Site Backends
and get them from a SiteBackend registry.  For now, using a singleton list.
"""

backends = []


def get_backend(site=None):
    global backends
    if not backends:
        backends.append(Backend())
    return backends[0]
