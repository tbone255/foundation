from rest_framework.metadata import BaseMetadata
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.core import serializers
import json

class ReactMetadata(BaseMetadata):


	def generate_field_json(self, field):
		field_dict = {}
		field_dict['class_name'] = field.__class__.__name__
		field_dict['name'] = field.name 
		
		form_field = field.formfield()

		if form_field:
			field_dict['type'] = (form_field.widget.__class__.__name__)

		return field_dict

	def determine_metadata(self, request, view):

		#ModelSerializer has a model field in its Meta class
		view_model = view.serializer_class.Meta.model

		#Using _meta (instance of Django's Option class), can get fields
		model_fields = view_model._meta.get_fields()

		fields = []
		for field in model_fields:
			fields.append(self.generate_field_json(field))
		fields_dict = {
			'fields': fields
		}

		return fields_dict