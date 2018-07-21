from django.core import checks
from django.db import models


class PasswordField(models.CharField):
    def __init__(self, *args, **kwargs):
        super(PasswordField, self).__init__(*args, **kwargs)

    def _check_max_length_attribute(self, **kwargs):
        if self.max_length is None:
            return [
                checks.Error(
                    'PasswordFields must define a "max_length" attribute.',
                    obj=self,
                    id='fields.E120',
                )
            ]
        elif (not isinstance(self.max_length, int) or isinstance(self.max_length, bool) or
                self.max_length <= 0):
            return [
                checks.Error(
                    '"max_length" must be a positive integer.',
                    obj=self,
                    id='fields.E121',
                )
            ]
        else:
            return []

    def get_internal_type(self):
        return 'PasswordField'

    def db_type(self, connection):
        return 'string'
