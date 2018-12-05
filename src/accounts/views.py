from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import (
                                    authenticate,
                                    get_user_model,
                                    login,
                                    logout,
                            )
from .forms import UserLoginForm, UserRegisterForm


def login_view(request):
    title = "Login"
    next_page = request.GET.get("next")
    print(next_page)
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(username=username, password=password)
        login(request, user)
        if next_page:
            return HttpResponseRedirect(next_page)
        return HttpResponseRedirect("/")

    context = {
                "form": form,
                "title": title,
    }
    return render(request, "form.html", context)


def register_view(request):
    title = "Register"
    next_page = request.GET.get("next")
    form = UserRegisterForm(request.POST or None)
    if form.is_valid():
        user = form.save(commit=False)
        password = form.cleaned_data.get("password")
        user.set_password(password)
        user.save()
        login(request, user)
        if next_page:
            return HttpResponseRedirect(next_page)
        return HttpResponseRedirect("/")

    context = {
                "title": title,
                "form": form
    }
    return render(request, "form.html", context)


def logout_view(request):
    logout(request)
    return HttpResponseRedirect("/")
    return render(request, "form.html", {})
