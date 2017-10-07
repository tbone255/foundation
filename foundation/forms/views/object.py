# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import router
from django.forms.models import _get_foreign_key
from django.utils.encoding import force_text
from django.views.generic import edit

from django import forms
from ...utils import get_deleted_objects

from ...backend import views
from .base import ControllerTemplateMixin
from .components import BaseModelFormMixin
from foundation.utils import flatten_fieldsets


__all__ = 'AddView', 'EditView', 'DisplayView', 'DeleteView'


class ObjectMixin(views.ObjectMixin):

    def get_success_url(self):
        return self.get_url('list')


class DeleteView(ObjectMixin, ControllerTemplateMixin, edit.BaseDeleteView):

    mode = 'delete'
    mode_title = 'delete'

    def get_context_data(self, **kwargs):
        object_name = force_text(self.object._meta.verbose_name)

        # Populate deleted_objects, a data structure of all related objects that
        # will also be deleted.
        (deleted_objects, model_count, perms_needed, protected) = get_deleted_objects(
            [self.object], self.object._meta, self.request.user,
            self.backend, router.db_for_write(self.model))

        kwargs.update(
            object=self.object,
            object_name=object_name,
            deleted_objects=deleted_objects,
            model_count=dict(model_count).items(),
        )
        return super(DeleteView, self).get_context_data(**kwargs)


class ProcessFormView(BaseModelFormMixin, ObjectMixin, ControllerTemplateMixin,
                      edit.ModelFormMixin, edit.ProcessFormView):
    """ Single-Object ModelForm View Mixin """

    def handle_common(self, handler, request, *args, **kwargs):
        handler = super(ProcessFormView, self).handle_common(
            handler, request, *args, **kwargs)
        self.object = None if self.add else self.get_object()
        self.form = self.get_form()
        return handler

    def get_inline_formsets(self, obj):
        """
        Return the InlineFormSet for this View via the ViewChild.
        TODO: Better handle the case where of no child controller (e.g. a check)
        """
        obj = None if self.add else self.object
        # we will only generate formsets for the fields specified for this view
        fields = flatten_fieldsets(self.get_fieldsets(self.mode))
        inline_formsets = {}
        for name, view_child in self.view_children.items():
            # do not make the inline formset if not an accessible form field
            if name not in fields:
                continue
            inline_formsets[name] = view_child.get_formset(obj=obj)
        return inline_formsets

    def get(self, request, *args, **kwargs):
        self.inline_formsets = self.get_inline_formsets(self.object)
        return super(ProcessFormView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if self.form.is_valid():
            form_validated = True
            new_object = self.save_form(change=not self.add)
        else:
            form_validated = False
            new_object = self.form.instance
        new_object._controller = self
        self.inline_formsets = self.get_inline_formsets(new_object)

        # val all formsets *first* to ensure we report them when form invalid
        if forms.all_valid(self.inline_formsets.values()) and form_validated:
            self.object = new_object
            self.save_model(not self.add)
            self.save_related(not self.add)
            return self.form_valid(self.form)
        else:
            return self.form_invalid(self.form)

    def get_media(self):
        media = super(ProcessFormView, self).get_media()
        media += self.form.media
        for inline_formset in self.inline_formsets.values():
            media += inline_formset.media
        return media

    def get_context_data(self, **kwargs):
        # from render_change_form
        request = self.request
        opts = self.model._meta
        app_label = opts.app_label
        # preserved_filters = self.get_preserved_filters(request)
        # form_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, form_url)

        # from changeform_view
        object_id = None
        # review
        if hasattr(self.object, 'pk') and '_saveasnew' not in request.POST:
            object_id = self.object.pk
        add = object_id is None

        kwargs.update({
            'form': self.form,
            'object_id': object_id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            preserved_filters=self.get_preserved_filters(request),
            # 'has_file_field': True,  # FIXME - this should check if form or formsets have a FileField,
            # 'form_url': form_url,
            # 'content_type_id': get_content_type_for_model(self.model).pk,
            # is_popup=(IS_POPUP_VAR in request.POST or
            #           IS_POPUP_VAR in request.GET),
            # 'to_field': to_field,
            # errors=helpers.AdminErrorList(form, formsets),
        })

        return super(ProcessFormView, self).get_context_data(**kwargs)


class AddView(ProcessFormView):

    mode = 'add'
    mode_title = 'add a'

        if IS_POPUP_VAR in request.POST:
            to_field = request.POST.get(TO_FIELD_VAR)
            if to_field:
                attr = str(to_field)
            else:
                attr = obj._meta.pk.attname
            value = obj.serializable_value(attr)
            popup_response_data = json.dumps({
                'value': str(value),
                'obj': str(obj),
            })
            return TemplateResponse(request, self.popup_response_template or [
                'admin/%s/%s/popup_response.html' % (opts.app_label, opts.model_name),
                'admin/%s/popup_response.html' % opts.app_label,
                'admin/popup_response.html',
            ], {
                'popup_response_data': popup_response_data,
            })

        elif "_continue" in request.POST or (
                # Redirecting after "Save as new".
                "_saveasnew" in request.POST and self.save_as_continue and
                self.has_change_permission(request, obj)
        ):
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            if post_url_continue is None:
                post_url_continue = obj_url
            post_url_continue = add_preserved_filters(
                {'preserved_filters': preserved_filters, 'opts': opts},
                post_url_continue
            )
            return HttpResponseRedirect(post_url_continue)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was added successfully.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            return self.response_post_save_add(request, obj)


    def sucess:
            self.message_user(request, msg, messages.SUCCESS)


class EditView(ProcessFormView):

    mode = 'edit'
    mode_title = 'Editing'

    _saveasnew

    def sucess:



        if "_continue" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = request.path
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_saveasnew" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was added successfully. You may edit it again below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:%s_%s_change' %
                                   (opts.app_label, opts.model_name),
                                   args=(obj.pk,),
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        elif "_addanother" in request.POST:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully. You may add another {name} below.'),
                **msg_dict
            )
            self.message_user(request, msg, messages.SUCCESS)
            redirect_url = reverse('admin:%s_%s_add' %
                                   (opts.app_label, opts.model_name),
                                   current_app=self.admin_site.name)
            redirect_url = add_preserved_filters({'preserved_filters': preserved_filters, 'opts': opts}, redirect_url)
            return HttpResponseRedirect(redirect_url)

        else:
            msg = format_html(
                _('The {name} "{obj}" was changed successfully.'),
                **msg_dict
            )


            
            
            self.message_user(request, msg, messages.SUCCESS)



class DisplayView(ProcessFormView):

    mode = 'display'
    mode_title = ''
