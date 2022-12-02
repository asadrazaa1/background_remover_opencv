from django.db import models


class ProcessedImage(models.Model):
    file = models.FileField(upload_to='processed_images')

    class Meta:
        verbose_name = "1 - ProcessedImage"
        verbose_name_plural = "1 - ProcessedImages"
