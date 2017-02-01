from django.shortcuts import render, redirect

from .forms import LoginForm


def login(request):

    form = LoginForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        request.session['username'] = form.cleaned_data['username']

        Account.objects.get_or_create(username=request.session['username'])

        return redirect('portfolio.views.home')

    return render(request, 'auth/login.html', {'form': form})


def logout(request):

    request.session['username'] = ''    

    return render(request, 'auth/login.html') 
