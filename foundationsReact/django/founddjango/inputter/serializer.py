from drf import fields
from rest_framework import serializers
from inputter.models import Inputter


class InputterSerializer(serializers.ModelSerializer):

    password = fields.PasswordField()

    class Meta:
        model = Inputter

        fields = ('title', 'password', 'exists')
