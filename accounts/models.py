from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):          # ← siz qoldirgan yagona model
    user     = models.OneToOneField(User,
                                    on_delete=models.CASCADE,
                                    related_name='profile')

    # --- rasmini ko‘rsatish uchun ---
    avatar   = models.ImageField(upload_to='avatars/',
                                 blank=True, null=True)

    # --- HOZIR yo‘qligi sababli xato bergan maydonlar ---
    phone    = models.CharField(max_length=20, blank=True)
    position = models.CharField(max_length=100, blank=True)
    bio      = models.TextField(blank=True)

    def __str__(self):
        return self.user.username
