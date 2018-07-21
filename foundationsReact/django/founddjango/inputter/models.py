from django.db import models
from drf import models as custom_models


class Inputter(models.Model):
    title = models.CharField(max_length=50, blank=False, help_text='test', default='')
    password = custom_models.PasswordField(max_length=50, blank=True, help_text='secret dont ', default='password1')
    exists = models.BooleanField(default=True)
