import os

from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.contrib.auth.models import User

import feedparser

from .models import SourceRSS, NewsItem, Comments
from .utils import add_news_items, rss_parser
from .forms import SourceForm, CommentForm


class SourceRSSModelTest(TestCase):

    def setUp(self):
        User.objects.create_user('test', 'test@email.com', 'test1234')
        self.user = User.objects.get(username='test')
        self.source = SourceRSS.objects.create(user=self.user, source_name='test', source_url='')

    def test_create_sourcerss_object(self):
        self.assertTrue(SourceRSS.objects.create(user=self.user, source_name='test', source_url=''))

    def test_user_label(self):
        field_label = self.source._meta.get_field('user').verbose_name
        self.assertEquals(field_label, 'user')

    def test_source_name_label(self):
        field_label = self.source._meta.get_field('source_name').verbose_name
        self.assertEquals(field_label, 'source name')

    def test_source_url_label(self):
        field_label = self.source._meta.get_field('source_url').verbose_name
        self.assertEquals(field_label, 'source url')

    def test_str_method(self):
        expected = self.source.source_name + ': ' + self.source.source_url
        self.assertEquals(expected, str(self.source))


class NewsItemModelTest(TestCase):

    def setUp(self):
        User.objects.create_user('test', 'test@email.com', 'test1234')
        self.user = User.objects.get(username='test')
        self.source = SourceRSS.objects.create(user=self.user, source_name='test', source_url='')
        self.news = NewsItem.objects.create(source=self.source, title='Test title', summary='Test summary', link='')

    def test_create_newsitem_object(self):
        self.assertTrue(NewsItem.objects.create(source=self.source, title='Test', summary='Test', link=''))

    def test_newsitem_source_label(self):
        field_label = self.news._meta.get_field('source').verbose_name
        self.assertEquals(field_label, 'source')

    def test_newsitem_title_label(self):
        field_label = self.news._meta.get_field('title').verbose_name
        self.assertEquals(field_label, 'title')

    def test_newsitem_summary_label(self):
        field_label = self.news._meta.get_field('summary').verbose_name
        self.assertEquals(field_label, 'summary')

    def test_newsitem_link_label(self):
        field_label = self.news._meta.get_field('link').verbose_name
        self.assertEquals(field_label, 'link')

    def test_str_method(self):
        expected = self.news.source.source_name + ': ' + self.news.title
        self.assertEquals(expected, str(self.news))


class CommentsModelTest(TestCase):

    def setUp(self):
        User.objects.create_user('test', 'test@email.com', 'test1234')
        self.user = User.objects.get(username='test')
        self.source = SourceRSS.objects.create(user=self.user, source_name='test', source_url='')
        self.news = NewsItem.objects.create(source=self.source, title='Test title', summary='Test summary', link='')
        self.comment = Comments.objects.create(news_item=self.news, user=self.user, comment='Test comment')

    def test_create_comment_object(self):
        self.assertTrue(Comments.objects.create(news_item=self.news, user=self.user, comment='Test'))

    def test_comment_newsitem_label(self):
        field_label = self.comment._meta.get_field('news_item').verbose_name
        self.assertEquals(field_label, 'news item')

    def test_comment_user_label(self):
        field_label = self.comment._meta.get_field('user').verbose_name
        self.assertEquals(field_label, 'user')

    def test_comment_comment_label(self):
        field_label = self.comment._meta.get_field('comment').verbose_name
        self.assertEquals(field_label, 'comment')

    def test_str_method(self):
        expected = self.comment.user.username + ': ' + self.comment.comment
        self.assertEquals(expected, str(self.comment))


class NewsfeedViewTests(TestCase):

    def setUp(self):
        self.not_logged_in_redirect = '/login/?next='
        User.objects.create_user('test', 'test@email.com', 'test1234')
        self.user = User.objects.get(username='test')
        self.source = SourceRSS.objects.create(user=self.user, source_name='test', source_url='')
        self.news = NewsItem.objects.create(source=self.source, title='Test title', summary='Test summary', link='')
        self.comment = Comments.objects.create(news_item=self.news, user=self.user, comment='Test comment')

    def test_newsfeed_all_view(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:newsfeed', args=['all']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsfeed/newsfeed.html')

    def test_newsfeed_all_view_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:newsfeed', args=['all']))
        self.assertRedirects(response, self.not_logged_in_redirect + reverse('newsfeed:newsfeed', args=['all']))

    def test_newsfeed_favorites_view(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:newsfeed', args=['favorites']))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsfeed/newsfeed.html')

    def test_newsfeed_favorites_view_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:newsfeed', args=['favorites']))
        self.assertRedirects(response, self.not_logged_in_redirect + reverse('newsfeed:newsfeed', args=['favorites']))

    def test_newsfeed_comments(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:comments', args=[self.news.pk]), {'Comment': 'Test comment'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsfeed/comments.html')

    def test_newsfeed_comments_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:comments', args=[self.news.pk]), {'Comment': 'Test comment'})
        self.assertEqual(response.status_code, 302)

    def test_newsfeed_like_comment(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:like_comment', args=[self.comment.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url='/newsfeed/' + str(self.news.pk) + '/comments/')

    def test_newsfeed_like_comment_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:like_comment', args=[self.comment.pk]))
        self.assertRedirects(response, self.not_logged_in_redirect + reverse('newsfeed:like_comment',
                                                                             args=[self.comment.pk]))

    def test_newsfeed_favorite(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:favorite', args=[self.news.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url='/newsfeed/all/')

    def test_newsfeed_favorite_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:favorite', args=[self.news.pk]))
        self.assertRedirects(response, self.not_logged_in_redirect + reverse('newsfeed:favorite', args=[self.news.pk]))

    def test_newsfeed_list_sources(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:list_sources'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsfeed/sources.html')

    def test_newsfeed_list_sources_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:list_sources'))
        self.assertRedirects(response, self.not_logged_in_redirect + reverse('newsfeed:list_sources'))

    def test_newsfeed_add_source(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:add_source'), {'Source name': 'Test', 'Source url': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'newsfeed/add_source.html')

    def test_newsfeed_add_source_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:add_source'), {'Source name': 'Test', 'Source url': ''})
        self.assertEqual(response.status_code, 302)

    def test_newsfeed_delete_source(self):
        self.client.login(username='test', password='test1234')
        response = self.client.get(reverse('newsfeed:delete_source', args=[self.source.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response=response, expected_url='/newsfeed/sources/')

    def test_newsfeed_delete_source_if_not_logged_in(self):
        response = self.client.get(reverse('newsfeed:delete_source', args=[self.source.pk]))
        self.assertEqual(response.status_code, 302)


class NewsfeedFormsTests(TestCase):

    def test_source_form_valid(self):
        form_data = {'source_name': 'Test', 'source_url': 'http://url.com/rss/'}
        form = SourceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_source_form_invalid(self):
        form_data = {'source_name': 'Test', 'source_url': 123}
        form = SourceForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_comments_form_valid(self):
        form_data = {'comment': 'Test'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comments_form_invalid(self):
        form_data = {'comment': ''}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())


class NewsfeedUtilsTests(TransactionTestCase):

    def setUp(self):
        User.objects.create_user('test', 'test@email.com', 'test1234')
        self.user = User.objects.get(username='test')
        self.source = SourceRSS.objects.create(user=self.user, source_name='test', source_url='')

    def test_add_news_items_unique_entry(self):
        path = os.path.abspath('newsfeed/unique_entry.xml')
        item = feedparser.parse(path).entries
        add_news_items(item, self.source)
        result = NewsItem.objects.filter(title='RSS Tutorial').count()
        self.assertEqual(result, 1)

    def test_add_news_items_duplicate_entry(self):
        path = os.path.abspath('newsfeed/duplicate_entry.xml')
        item = feedparser.parse(path).entries
        add_news_items(item, self.source)
        result = NewsItem.objects.filter(title='RSS Tutorial').count()
        self.assertEqual(result, 1)

    def test_add_last_modified_tag_to_source(self):
        """
        Add last_modified_tag to source for rss feeds that provide an ETag/last-modified
        """
        self.source.source_url = 'http://rss.nytimes.com/services/xml/rss/nyt/Europe.xml'
        self.source.save()
        rss_parser([self.source.pk])
        self.source = SourceRSS.objects.get(source_name='test')
        self.assertTrue(self.source.last_modified_tag)
        self.assertTrue(self.source.last_modified_value)

    def test_no_last_modified_tag_in_request(self):
        """
        Don't change last_modified_tag in source for rss feeds that don't provide an ETag/last-modified
        """
        self.source.source_url = 'http://feeds.washingtonpost.com/rss/sports'
        self.source.save()
        rss_parser([self.source.pk])
        self.source = SourceRSS.objects.get(source_name='test')
        self.assertFalse(self.source.last_modified_tag)
        self.assertFalse(self.source.last_modified_value)

    def test_get_last_modified_items(self):
        """
        Only retrieve new items from the rss feed
        """
        self.source.source_url = 'http://rss.nytimes.com/services/xml/rss/nyt/Europe.xml'
        self.source.save()
        rss_parser([self.source.pk])
        initial_items = NewsItem.objects.all()
        rss_parser([self.source.pk])
        new_items = NewsItem.objects.all()
        self.assertTrue(len(new_items) == len(initial_items))
