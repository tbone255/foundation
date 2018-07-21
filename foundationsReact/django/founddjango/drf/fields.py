from django.utils.functional import lazy
from django.utils import six
from rest_framework.compat import (
    MaxLengthValidator,
    MinLengthValidator,
)
from rest_framework.fields import Field, empty
from django.utils.translation import ugettext_lazy as _


class PasswordField(Field):
    default_error_messages = {
        'invalid': _('Not a valid string.'),
        'blank': _('This field may not be blank.'),
        'max_length': _('Ensure this field has no more than {max_length} characters.'),
        'min_length': _('Ensure this field has at least {min_length} characters.')
    }
    initial = ''

    def __init__(self, **kwargs):
        print(kwargs)
        self.allow_blank = kwargs.pop('allow_blank', False)
        self.trim_whitespace = kwargs.pop('trim_whitespace', True)
        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)
        super(PasswordField, self).__init__(**kwargs)
        if self.max_length is not None:
            message = lazy(
                self.error_messages['max_length'].format,
                six.text_type)(max_length=self.max_length)
            self.validators.append(
                MaxLengthValidator(self.max_length, message=message))
        if self.min_length is not None:
            message = lazy(
                self.error_messages['min_length'].format,
                six.text_type)(min_length=self.min_length)
            self.validators.append(
                MinLengthValidator(self.min_length, message=message))

    def run_validation(self, data=empty):
        # Test for the empty string here so that it does not get validated,
        # and so that subclasses do not need to handle it explicitly
        # inside the `to_internal_value()` method.
        if data == '' or (self.trim_whitespace and six.text_type(data).strip() == ''):
            if not self.allow_blank:
                self.fail('blank')
            return ''
        return super(PasswordField, self).run_validation(data)

    def to_internal_value(self, data):
        # We're lenient with allowing basic numerics to be coerced into strings,
        # but other types should fail. Eg. unclear if booleans should represent as `true` or `True`,
        # and composites such as lists are likely user error.
        if isinstance(data, bool) or not isinstance(data, six.string_types + six.integer_types + (float,)):
            self.fail('invalid')
        value = six.text_type(data)
        return value.strip() if self.trim_whitespace else value

    def to_representation(self, value):
        return six.text_type(value)
