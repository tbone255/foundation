# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.views.generic import list

from .base import ControllerTemplateMixin
from .components import FormSetMixin
from ...backend.views import ListMixin

__all__ = 'ListView',


class ListView(FormSetMixin, ControllerTemplateMixin, ListMixin, list.ListView):
    """ Multiple-Object ModelFormSet View Mixin """

    mode_title = 'all'

    def handle_common(self, handler, request, *args, **kwargs):
        handler = super(FormSetMixin, self).handle_common(
            handler, request, *args, **kwargs
        )

        if self.is_popup:
            self.list_editable = ()

        parent_obj = (self.view_parent.get_object()
                      if self.view_parent
                      else None)

        # feed the par-reduced queryset to formset, which will in turn FK
        # constrain it, as applicable
        self.formset = self.get_formset(
            obj=parent_obj,
            queryset=self.queryset
        )

        return handler

    def get_context_data(self, **kwargs):
        kwargs.update({
            'formset': self.formset,
        })
        return super(ListView, self).get_context_data(**kwargs)

    # self.list_filter = list_filter
    # self.preserved_filters = controller.get_preserved_filters(view)
    # get from controller
    # self.list_display = list_display
    # self.list_display_links = list_display_links
    # self.date_hierarchy = date_hierarchy
    # self.search_fields = search_fields
    # self.list_select_related = list_select_related
    # self.list_per_page = list_per_page
    # self.list_max_show_all = list_max_show_all

    # Get search parameters from the query string.

    '''
    def get_list_display(self, request):
        """
        Return a sequence containing the fields to be displayed on the
        changelist.
        """
        return self.list_display

    def get_list_display_links(self, request, list_display):
        """
        Return a sequence containing the fields to be displayed as links
        on the changelist. The list_display parameter is the list of fields
        returned by get_list_display().
        """
        if self.list_display_links or self.list_display_links is None or not list_display:
            return self.list_display_links
        else:
            # Use only the first item in list_display as link
            return list(list_display)[:1]
    def get_list_select_related(self, request):
        """
        Returns a list of fields to add to the select_related() part of the
        changelist items query.
        """
        return self.list_select_related


    def get_changeform_initial_data(self, request):
        """
        Get the initial form data.
        Unless overridden, this populates from the GET params.
        """
        initial = dict(request.GET.items())
        for k in initial:
            try:
                f = self.model._meta.get_field(k)
            except FieldDoesNotExist:
                continue
            # We have to special-case M2Ms as a list of comma-separated PKs.
            if isinstance(f, models.ManyToManyField):
                initial[k] = initial[k].split(",")
        return initial

    def lookup_allowed(self, lookup, value):
        from django.contrib.admin.filters import SimpleListFilter

        model = self.model
        # Check FKey lookups that are allowed, so that popups produced by
        # ForeignKeyRawIdWidget, on the basis of ForeignKey.limit_choices_to,
        # are allowed to work.
        for l in model._meta.related_fkey_lookups:
            # As ``limit_choices_to`` can be a callable, invoke it here.
            if callable(l):
                l = l()
            for k, v in widgets.url_params_from_lookup_dict(l).items():
                if k == lookup and v == value:
                    return True

        relation_parts = []
        prev_field = None
        for part in lookup.split(LOOKUP_SEP):
            try:
                field = model._meta.get_field(part)
            except FieldDoesNotExist:
                # Lookups on non-existent fields are ok, since they're ignored
                # later.
                break
            # It is allowed to filter on values that would be found from local
            # model anyways. For example, if you filter on employee__department__id,
            # then the id value would be found already from employee__department_id.
            if not prev_field or (prev_field.concrete and
                                  field not in prev_field.get_path_info()[-1].target_fields):
                relation_parts.append(part)
            if not getattr(field, 'get_path_info', None):
                # This is not a relational field, so further parts
                # must be transforms.
                break
            prev_field = field
            model = field.get_path_info()[-1].to_opts.model

        if len(relation_parts) <= 1:
            # Either a local field filter, or no fields at all.
            return True
        clean_lookup = LOOKUP_SEP.join(relation_parts)
        valid_lookups = [self.date_hierarchy]
        for filter_item in self.list_filter:
            if isinstance(filter_item, type) and issubclass(filter_item, SimpleListFilter):
                valid_lookups.append(filter_item.parameter_name)
            elif isinstance(filter_item, (list, tuple)):
                valid_lookups.append(filter_item[0])
            else:
                valid_lookups.append(filter_item)
        return clean_lookup in valid_lookups

    def to_field_allowed(self, request, to_field):
        """
        Returns True if the model associated with this admin should be
        allowed to be referenced by the specified field.
        """
        opts = self.model._meta

        try:
            field = opts.get_field(to_field)
        except FieldDoesNotExist:
            return False

        # Always allow referencing the primary key since it's already possible
        # to get this information from the change view URL.
        if field.primary_key:
            return True

        # Allow reverse relationships to models defining m2m fields if they
        # target the specified field.
        for many_to_many in opts.many_to_many:
            if many_to_many.m2m_target_field_name() == to_field:
                return True

        # Make sure at least one of the models registered for this site
        # references this field through a FK or a M2M relationship.
        registered_models = set()
        for model, admin in self.admin_site._registry.items():
            registered_models.add(model)
            for inline in admin.inlines:
                registered_models.add(inline.model)

        related_objects = (
            f for f in opts.get_fields(include_hidden=True)
            if (f.auto_created and not f.concrete)
        )
        for related_object in related_objects:
            related_model = related_object.related_model
            remote_field = related_object.field.remote_field
            if (any(issubclass(model, related_model) for model in registered_models) and
                    hasattr(remote_field, 'get_related_field') and
                    remote_field.get_related_field() == field):
                return True

        return False
    '''
