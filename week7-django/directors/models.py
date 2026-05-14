from django.db import models

class Director(models.Model):
  name = models.CharField(max_length=100)
  nationality = models.CharField(max_length=100)
  created_at = models.DateTimeField(auto_now_add=True)

