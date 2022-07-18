import base64
import uuid
from django.core.files.base import ContentFile
from rest_framework import serializers


class Base64FileField(serializers.FileField):
    """Custom field - декодирует base64 и сохраняет в файл"""
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, filestr = data.split(';base64,')
            extension = format.split('/')[-1]
            id = uuid.uuid4()
            data = ContentFile(base64.b64decode(filestr),
                               name=f'{id.urn[9:]}.{extension}')
        return super().to_internal_value(data)
        # super(Base64FileField, self).to_internal_value(data)
