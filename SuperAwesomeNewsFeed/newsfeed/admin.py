from django.contrib import admin
from .models import SourceRSS, NewsItem, Comments

admin.site.register(SourceRSS)
admin.site.register(NewsItem)
admin.site.register(Comments)
