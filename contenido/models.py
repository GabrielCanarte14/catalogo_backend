from django.db import models


class Genre(models.Model):
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class Books(models.Model):
    name = models.CharField(max_length=256)
    autor = models.CharField(max_length=256)
    pub_date = models.DateTimeField("date published")
    isbn = models.CharField(max_length=256)
    editorial = models.CharField(max_length=256)
    genre = models.ForeignKey(
        Genre, related_name="book", on_delete=models.CASCADE
    )

    def __str__(self):
        return self.name
