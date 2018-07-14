from django.db import models

# Create your models here.
class Inputter(models.Model):
	title = models.CharField(max_length=50, blank=False, default='')
	exists = models.BooleanField(default=True)
