from django.db import models
from django_softdelete.models import SoftDeleteModel


class BaseModel(SoftDeleteModel):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


DEFAULT_EXCLUDE_FIELDS = [
    "updated_at",
    "deleted_at",
    "restored_at",
    "transaction_id",
]
