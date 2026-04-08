from django.db import models



class Movie(models.Model):
  title = models.CharField(max_length=200)
  genre = models.CharField(max_length=100)
  rating = models.DecimalField(                     
        max_digits=3,
        decimal_places=1
    )
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.title} ({self.rating})"