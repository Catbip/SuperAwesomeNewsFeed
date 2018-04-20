import feedparser
from django.db import IntegrityError

from .models import SourceRSS, NewsItem


def rss_parser(sources_pks):
    """
    Takes a list of SourceRSS.pk and parses their urls.
    If the source has been parsed before, only gets the new items.

    sources is a dictionary containing the RSS url, an ETag or Last-Modified tag,
    and the value of the tag.
    """

    for key in sources_pks:
        source = SourceRSS.objects.get(pk=key)
        url = source.source_url
        tag = source.last_modified_tag
        value = source.last_modified_value

        if tag:
            # source has been parsed before
            if tag == 'ETag':
                items = feedparser.parse(url, etag=value)
                if items.status == 304:
                    continue
            else:
                items = feedparser.parse(url, modified=value)

        else:
            # source has never been parsed before or tags don't work for it
            items = feedparser.parse(url)
            try:
                source.last_modified_value = items.etag
                source.last_modified_tag = 'ETag'
                source.save()
            except (KeyError, AttributeError):
                try:
                    source.last_modified_value = items.modified
                    source.last_modified_tag = 'Last-Modified'
                    source.save()
                except (KeyError, AttributeError):
                    pass
        add_news_items(items.entries, source)


def add_news_items(items, source):
    """
    Adds parsed news items to the database.
    """
    for item in items:
        news_item = NewsItem()
        news_item.source = source
        news_item.title = item.title
        news_item.link = item.link
        try:
            news_item.summary = item.summary
        except AttributeError:
            news_item.summary = ""
        try:
            news_item.save()
        except IntegrityError:
            continue
