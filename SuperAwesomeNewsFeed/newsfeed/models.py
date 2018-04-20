from django.db import models
from django.contrib.auth.models import User


class SourceRSS(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_name = models.CharField(max_length=100)
    source_url = models.URLField()
    last_modified_tag = models.CharField(max_length=50, null=True, default=None)
    last_modified_value = models.TextField(null=True, default=None)

    def __str__(self):
        return self.source_name + ': ' + self.source_url


class NewsItem(models.Model):
    source = models.ForeignKey(SourceRSS, on_delete=models.CASCADE)
    title = models.CharField(max_length=250, unique=True)
    summary = models.TextField(max_length=500)
    link = models.URLField()
    favorite = models.BooleanField(default=False)

    def __str__(self):
        return self.source.source_name + ': ' + self.title


class Comments(models.Model):
    news_item = models.ForeignKey(NewsItem, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField(max_length=1000)
    date = models.DateField(auto_now=True)
    likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username + ': ' + self.comment
