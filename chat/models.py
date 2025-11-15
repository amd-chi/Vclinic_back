from user.models import User
from utils.base_models import BaseModel
from django.db import models


class Message(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    is_doctor_response = models.BooleanField(default=False)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_seen = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        "user.User",
        on_delete=models.SET_NULL,
        related_name="created_messages",
        null=True,
        blank=True,
    )
    # created_by = models.ForeignKey(
    #     "user.User",
    # )

    class Meta:
        indexes = [
            models.Index(fields=["user"]),
        ]
