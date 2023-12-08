from django.db import models


# Create your models here.
class Base(models.Model):
    id = models.AutoField(primary_key=True)
    is_active = models.BooleanField("Estado", default=True)
    created_at = models.DateField("Fecha de creación", auto_now_add=True)
    modified_at = models.DateField("Fecha de modificación", auto_now=True)
    deleted_at = models.DateField("Fecha de eliminación", null=True, blank=True)

    class Meta:
        abstract = True
        verbose_name = "Modelo base"
        verbose_name_plural = "Modelos base"
