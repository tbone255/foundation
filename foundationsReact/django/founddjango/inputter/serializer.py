from rest_framework import serializers
from inputter.models import Inputter

class InputterSerializer(serializers.ModelSerializer):
	
	class Meta:
		model = Inputter
		fields = ('title', 'exists') 
