# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.functional import cached_property
from rest_framework import renderers, routers, permissions
from .registry import Registry
from django.conf.urls import url
from collections import OrderedDict

__all__ = 'PageRouter', 'EmbedRouter', 'APIRouter'


class BackendMixin(object):  # Registry):

    '''
    backend = None
    viewsets = {}
    view_class_mixin = None

    '''

    def get_urls(self):
        """
        Use the registered viewsets to generate a list of URL patterns.
        This is a hard override of DRF that will allow us to lookup URLs via
        backend/app_config/controller-and-action.
        """
        ret = []

        for prefix, viewset, basename in self.registry:
            lookup = self.get_lookup_regex(viewset)
            routes = self.get_routes(viewset)

            for route in routes:

                # Only actions which actually exist on the viewset will be bound
                mapping = self.get_method_map(viewset, route.mapping)
                if not mapping:
                    continue

                # Build the url pattern
                regex = route.url.format(
                    prefix=prefix,
                    lookup=lookup,
                    trailing_slash=self.trailing_slash
                )

                # If there is no prefix, the first part of the url is probably
                #   controlled by project's urls.py and the router is in an app,
                #   so a slash in the beginning will (A) cause Django to give
                #   warnings and (B) generate URLS that will require using '//'.
                if not prefix and regex[:2] == '^/':
                    regex = '^' + regex[2:]

                view = viewset.as_view(mapping, **route.initkwargs)
                name = route.name.format(basename=basename)
                ret.append(url(regex, view, name=name))
                print(view, name, view.cls.controller)

        print(ret)
        return ret



class BaseFormRouter(BackendMixin, routers.SimpleRouter):

    default_renderers = (
        renderers.TemplateHTMLRenderer,
        # renderers.HTMLFormRenderer,  # TODO: Consider applications
    )

    # HARD OVERRIDE OF ROUTES REMOVES BASENAME FROM ROUTING TO ACCOM NAMESPACES
    routes = [
        # List route.
        routers.Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'list',
            },
            name='list',
            initkwargs={'suffix': 'List'},
        ),
        # List route.
        routers.Route(
            url=r'^{prefix}/add{trailing_slash}$',
            mapping={
                'get': 'create',
                'post': 'create',
            },
            name='add',
            initkwargs={'prefix': 'Add New'},
        ),
        # Detail route.
        routers.Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'partial_update',
            },
            name='detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Detail route.
        routers.Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'update',
                'post': 'update',
            },
            name='edit',
            initkwargs={'prefix': 'Editing'},
        ),
        # Detail route.
        routers.Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'destroy',
                'post': 'destroy',
            },
            name='delete',
            initkwargs={'prefix': 'Deleting'},
        ),
    ]

    def __init__(self, *args, **kwargs):
        if 'root_renderers' in kwargs:
            self.root_renderers = kwargs.pop('root_renderers')
        else:
            self.root_renderers = list(self.default_renderers)
        super(BaseFormRouter, self).__init__(*args, **kwargs)



class EmbedRouter(BaseFormRouter):
    pass


class PageRootView(object):  # views.APIView):
    """
    The default basic root view for DefaultRouter
    """
    _ignore_model_permissions = True
    schema = None  # exclude from schema
    api_root_dict = None

    def get(self, request, *args, **kwargs):
        # Return a plain {"name": "hyperlink"} response.
        ret = OrderedDict()
        namespace = request.resolver_match.namespace
        for key, url_name in self.api_root_dict.items():
            if namespace:
                url_name = namespace + ':' + url_name
            try:
                ret[key] = reverse(
                    url_name,
                    args=args,
                    kwargs=kwargs,
                    request=request,
                    format=kwargs.get('format', None)
                )
            except NoReverseMatch:
                # Don't bail out if eg. no list routes exist, only detail routes.
                continue

        return Response(ret)


class PageRouter(BaseFormRouter):

    include_root_view = False  # True
    root_view_name = 'index'
    RootView = PageRootView

    def get_index_view(self, urls=None):
        api_root_dict = OrderedDict()
        list_name = self.routes[0].name
        for prefix, viewset, basename in self.registry:
            api_root_dict[prefix] = list_name.format(basename=basename)

        return self.RootView.as_view(api_root_dict=api_root_dict)

    def get_urls(self):
        urls = super(PageRouter, self).get_urls()

        if self.include_root_view:
            view = self.get_index_view(urls=urls)
            root_url = url(r'^$', view, name=self.root_view_name)
            urls.append(root_url)

        return urls


class APIRouter(BackendMixin, routers.DefaultRouter):

    # HARD OVERRIDE OF ROUTES REMOVES BASENAME FROM ROUTING TO ACCOM NAMESPACES
    routes = [
        # List route.
        routers.Route(
            url=r'^{prefix}{trailing_slash}$',
            mapping={
                'get': 'list',
                'post': 'create'
            },
            name='list',
            initkwargs={'suffix': 'List'}
        ),
        # Dynamically generated list routes.
        # Generated using @list_route decorator
        # on methods of the viewset.
        routers.DynamicListRoute(
            url=r'^{prefix}/{methodname}{trailing_slash}$',
            name='{methodnamehyphen}',
            initkwargs={}
        ),
        # Detail route.
        routers.Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='detail',
            initkwargs={'suffix': 'Instance'}
        ),
        # Dynamically generated detail routes.
        # Generated using @detail_route decorator on methods of the viewset.
        routers.DynamicDetailRoute(
            url=r'^{prefix}/{lookup}/{methodname}{trailing_slash}$',
            name='{methodnamehyphen}',
            initkwargs={}
        ),
    ]

    def get_routes(self, viewset):
        ret = super(APIRouter, self).get_routes(viewset)
        # {basename}-list {'get': 'list', 'post': 'create'} ^{prefix}{trailing_slash}$
        # {basename}-detail {'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'} ^{prefix}/{lookup}{trailing_slash}$
        # for rt in ret:
        #     print(rt.name, rt.mapping, rt.url)
        return ret

    def get_lookup_regex(self, viewset, lookup_prefix=''):
        return super(APIRouter, self).get_lookup_regex(viewset, lookup_prefix)

    def get_urls(self):
        urls = super(APIRouter, self).get_urls()
        return urls

