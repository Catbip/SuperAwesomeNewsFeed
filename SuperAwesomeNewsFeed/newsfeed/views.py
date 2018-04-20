from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import SourceRSS, NewsItem, Comments
from .forms import SourceForm, CommentForm
from .utils import rss_parser


@login_required(login_url='/login/')
def newsfeed(request, sort_by):
    sources = list()
    for source in SourceRSS.objects.filter(user=request.user):
        sources.append(source.pk)

    rss_parser(sources)
    if sort_by == 'favorites':
        news = NewsItem.objects.filter(favorite=True)
    else:
        news = NewsItem.objects.all()

    context = {
        'news': news
    }

    return render(request, 'newsfeed/newsfeed.html', context)


@login_required(login_url='/login/')
def comments(request, news_id):
    news_item = get_object_or_404(NewsItem, pk=news_id)
    all_comments = Comments.objects.filter(news_item=news_item)

    form = CommentForm(request.POST or None)
    news_item = get_object_or_404(NewsItem, pk=news_id)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.user = request.user
        comment.news_item = news_item
        comment.save()

        return redirect('newsfeed:comments', news_id)

    context = {
        'news_item': news_item,
        'comments': all_comments,
        "form": form
    }

    return render(request, 'newsfeed/comments.html', context)


@login_required(login_url='/login/')
def like_comment(request, comment_id):
    comment = get_object_or_404(Comments, pk=comment_id)
    comment.likes += 1
    comment.save()

    return redirect('newsfeed:comments', comment.news_item.pk)


@login_required(login_url='/login/')
def favorite(request, news_id):
    news = get_object_or_404(NewsItem, pk=news_id)
    news.favorite = not news.favorite
    news.save()

    return redirect('newsfeed:newsfeed', 'all')


@login_required(login_url='/login/')
def list_sources(request):
    sources = SourceRSS.objects.all()
    context = {
        'sources_list': sources
    }

    return render(request, 'newsfeed/sources.html', context)


@login_required(login_url='/login/')
def add_source(request):
    form = SourceForm(request.POST or None)
    if form.is_valid():
        source = form.save(commit=False)
        source.user = request.user
        source.save()

        return redirect('newsfeed:list_sources')

    context = {
        "form": form,
    }

    return render(request, 'newsfeed/add_source.html', context)


@login_required(login_url='/login/')
def delete_source(request, source_id):
    source = SourceRSS.objects.get(pk=source_id)
    source.delete()

    return redirect('newsfeed:list_sources')
