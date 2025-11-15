from django.db import models
from ckeditor.fields import RichTextField


# Create your models here.
class AppMessage(models.Model):
    content = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    users_read = models.ManyToManyField(
        "user.User", related_name="app_messages_read", null=True, blank=True
    )
