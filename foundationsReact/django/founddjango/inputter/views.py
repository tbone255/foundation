from django.shortcuts import render

from rest_framework import viewsets
from rest_framework.response import Response

from inputter.models import Inputter
from inputter.serializer import InputterSerializer

class InputterViewSet(viewsets.ModelViewSet):

	# Create your views here.
	queryset = Inputter.objects.all()
	serializer_class = InputterSerializer

	