from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse

from .forms import LoginForm


def login(request):

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        request.session['username'] = form.cleaned_data['username']

        return redirect('/')

    return render(request, 'authenticate/login.html', {'form': form})


def logout(request):

    request.session['username'] = ''    

    return render(request, 'authenticate/login.html') 
