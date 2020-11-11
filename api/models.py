from django.db import models
from datetime import datetime
import uuid


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, verbose_name="Name")
    namespace = models.CharField(max_length=120, verbose_name="NameSpace")
    timestamp = models.DateTimeField(default=datetime.now)
    value = models.IntegerField()

    def __str__(self):
        return '{} - {}: {}'.format(self.namespace, self.name, self.value)