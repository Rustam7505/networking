from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True # Bu model ma'lumotlar bazasida jadval yaratmaydi, balki boshqa modellarga meros beradi