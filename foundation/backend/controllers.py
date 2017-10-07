# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url, include
from django.core.paginator import Paginator

from .controller import BaseController
from .router import Router

__all__ = 'Controller',


class ModelOptions(object):
    """ Describes how to represent a Model for a Controller. """

    fields = None
    exclude = None
    fieldsets = None
    ordering = None


class PartialViewOptions(ModelOptions):
    """
    Describes inter-relationships needed for partial view composition.
    NOTE: This is expected to be the base for FormOptions, and thus, Inlines.
    """

    fk_name = None
    slug_field = 'slug'
    model = None
    parent = None


class ViewOptions(PartialViewOptions):
    """ Describes configurable options only for URL-accessible base Views. """

    children = ()
    inlines = ()

    # pagination options
    paginator_class = Paginator
    list_per_page = 20
    list_max_show_all = 200
    show_full_result_count = True

    # search options
    search_fields = ()
    search_by_field = False  # when True, query from field names vs. SEARCH_VAR

    # save options
    save_as = False
    save_as_continue = True
    save_on_top = False

    # action options -- list and object?
    actions = []
    action_form = helpers.ActionForm
    actions_on_top = True
    actions_on_bottom = False
    actions_selection_counter = True
    checks_class = ModelAdminChecks

    preserve_filters = True

    # unmerged options
    list_display = ('__str__',)
    list_display_links = ()
    list_select_related = False
    list_editable = ()
    date_hierarchy = None

    # Custom templates (designed to be over-ridden in subclasses)
    add_form_template = None
    change_form_template = None
    change_list_template = None
    delete_confirmation_template = None
    delete_selected_confirmation_template = None
    object_history_template = None
    popup_response_template = None


class ControllerOptions(ViewOptions):
    """ Configurable options for registered controllers. """

    checks_class = None
    registrar = None
    public_modes = ()


    """
    list_display = ('__unicode__',)
    list_display_links = ()
    list_select_related = False
    list_editable = ()


    def update(self, attrs):
        for key in dir(self):
            if not key.startswith('_'):
                setattr(self, key, attrs.pop(key, getattr(self, key)))

    def __init__(self, attrs):
        super(ControllerOptions, self).__init__()
        self.update(attrs)

    def __getattribute__(self, name):
        '''
        When an attribute is not found, attempt to pass-through to the Model
        Meta (Options).
        '''

        super_getattr = super(ControllerOptions, self).__getattribute__
        model = super_getattr('model')
        try:
            return super_getattr(name)
        except AttributeError as e:
            try:
                return getattr(model._meta, name)
            except AttributeError:
                raise e
    """


class Controller(ControllerOptions, Router, BaseController):
    """
    Controllers need the ability to:
    a) generate the URLs needed for the Backend
    b) generate the JIT (View, Inline, and Parent) Controller for each View
    """

    def __init__(self, parent, registrar=None):
        """
        Initializes a Model Controller for eventual registration as a Backend
        controller or a Controller sub-controller.
        :param parent: the Backend or Controller instance from which
            this Controller was created
        :param registrar: the Backend or Controller instance under which
            this Controller is to be registered
        """

        # only registered Controller will be aware of their registered parent
        from .base import Backend
        if isinstance(parent, Backend):
            if registrar and registrar != parent:
                raise ValueError('"registrar" cannot be set to non-backend when'
                                 ' "backend" is also set.')
            self.registrar = backend = parent
        else:
            if not registrar:
                registrar = parent
            backend = parent.backend
            self.parent = parent
            self.registrar = registrar

        # this Controller will be its own registered controller
        super(Controller, self).__init__(backend=backend, controller=self)

    @property
    def is_root(self):
        return self.parent is None

    @property
    def is_local_root(self):
        return self.registrar is self.backend

    def check(self, **kwargs):
        return (self.checks_class().check(self, **kwargs)
                if self.checks_class else [])

    def get_associated_queryset(self):
        queryset = self.model._default_manager.get_queryset()
        queryset.attach(controller=self)

    def get_view_parent(self, view, kwargs):
        view_parent = view.view_parent_class(
            view=view, controller=self, kwargs=kwargs)
        view_parent.__class__.__name__ =  str('{}ViewParent'.format(
            view_parent.controller.model.__name__
        ))
        return view_parent

    def get_view_child(self, view):
        view_child = view.view_child_class(view=view, controller=self)
        return view_child

    def get_urlpatterns(self):

        # gets the set of named urlpatterns from this controller's viewsets
        urlpatterns = super(Controller, self).get_urlpatterns(self)

        # gets the urlpatterns from each child and makes additional entries
        # in the patterns as needed
        for child_controller_class in self.children:
            child_model = child_controller_class.model
            child_controller = self.get_registered_controller(child_model)
            child_namespace = child_controller.model_namespace
            child_prefix = child_controller.url_prefix

            # get named patterns from child and extend
            child_urlpatterns = child_controller.get_urlpatterns()
            for name, patterns in child_urlpatterns.items():
                urlpatterns[name].append(
                    url(r'^(?P<{lookup}>[-\w]+)/{prefix}'.format(
                            lookup=self.model_lookup,
                            prefix=child_prefix
                        ),
                        include((patterns, child_namespace))
                    ),
                )

        return urlpatterns

    def get_index_url(self):
        return self.get_url('index')

    def get_url_from_object(self, mode, obj=None, route=None, **kwargs):
        """
        TODO: This is a placeholder for a means of a fully deriving a URL from a
        non-View Controller given an obj.  This is potentially very expensive,
        having to follow an undefined number of FKs, and would be compelled to
        fail if there were any "unanswerables" (e.g. many-to-one) relationships
        in the chain.
        """
        raise NotImplementedError
