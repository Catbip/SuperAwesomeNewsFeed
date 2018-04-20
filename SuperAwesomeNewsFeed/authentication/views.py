from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegisterForm


def index(request):
    if request.user.is_authenticated:
        return redirect('newsfeed:newsfeed', 'all')
    else:
        return redirect('authentication:login_user')


def register(request):
    form = RegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        user.set_password(password)
        user.save()
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('newsfeed:newsfeed', 'all')

    context = {'form': form}

    return render(request, 'authentication/registration_form.html', context)


def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('newsfeed:newsfeed', 'all')
        else:
            return render(request, 'authentication/login_form.html', {'error_message': 'Invalid login'})
    return render(request, 'authentication/login_form.html')


def logout_user(request):
    logout(request)
    return redirect('authentication:login_user')
