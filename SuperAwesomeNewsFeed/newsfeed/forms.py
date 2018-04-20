from django import forms

from .models import SourceRSS, Comments


class SourceForm(forms.ModelForm):
    class Meta:
        model = SourceRSS
        fields = ['source_name', 'source_url']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ['comment']
