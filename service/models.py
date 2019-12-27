# Create your models here.
import os

from django.db import models
from django.utils import timezone

from console_main import settings
from login import models as loginModels


class UploadFile(models.Model):
    did = models.CharField(max_length=64)
    uploaded_file = models.FileField(upload_to='user_files')

    def delete(self, *args, **kwargs):
        os.remove(os.path.join(settings.MEDIA_ROOT, self.uploaded_file.name))
        super(UploadFile, self).delete(*args, **kwargs)


class UserServiceSessionVars(models.Model):
    did = models.CharField(max_length=64)
    api_key = models.CharField(max_length=64)

    mnemonic_mainchain = models.CharField(max_length=300)
    private_key_mainchain = models.CharField(max_length=300)
    public_key_mainchain = models.CharField(max_length=300)
    address_mainchain = models.CharField(max_length=64)

    private_key_did = models.CharField(max_length=300)
    public_key_did = models.CharField(max_length=300)
    address_did = models.CharField(max_length=64)
    did_did = models.CharField(max_length=64)

    address_eth = models.CharField(max_length=64)
    private_key_eth = models.CharField(max_length=300)


class TrackUserService(models.Model):
    did = models.CharField(max_length=64)
    service = models.CharField(max_length=300)  # for internal views use only. (identifier)
    name = models.CharField(max_length=300)  # use to display name or description to user
    url = models.CharField(max_length=400)  # give the reverse url that would normally be in template(helps reduce code)
    last_visited = models.DateTimeField(default=timezone.now)
    number_visits = models.PositiveIntegerField(default=0)
