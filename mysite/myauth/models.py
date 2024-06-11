from django.contrib.auth.models import User
from django.db import models


def avatar_images_directory_path(instance: "Profile", filename: str) -> str:
    return "users/user_{pk}/avatars/{filename}".format(
        pk=instance.pk, filename=filename
    )


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar_image = models.ImageField(null=True, blank=True, upload_to=avatar_images_directory_path)
