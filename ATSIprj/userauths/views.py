from django.shortcuts import render, redirect
from userauths.forms import UserRegisterForm, ProfileForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.conf import settings

from userauths.models import Profile

User = settings.AUTH_USER_MODEL


def register_view(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST or None)
        if form.is_valid():
            new_user = form.save()
            username = form.cleaned_data.get("username")
            messages.success(request, f"Hey {username}, Your account was created successfully.")
            new_user = authenticate(username=form.cleaned_data.get('email'),
                                    password=form.cleaned_data.get('password1'))
            login(request, new_user)
            return redirect("core:index")

    else:
        form = UserRegisterForm()

    context = {
        'form': form,
    }

    return render(request, "userauths/sign-up.html", context)


def login_view(request):
    if request.user.is_authenticated:
        messages.warning(request, f"Hey you are already Logged In.")
        return redirect("core:index")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            user = authenticate(request, email=email, password=password)

            if user is not None:
                login(request, user)
                messages.success(request, "You are logged in.")
                next_url = request.GET.get("next", 'core:index')
                return redirect(next_url)
            else:
                messages.warning(request, "Wrong data. Check your email or password.")

        except:
            messages.warning(request, f"Wrong data. Check your email or password.")

    return render(request, "userauths/sign-in.html")


def logout_view(request):
    logout(request)
    messages.success(request, "You are logged out.")
    return redirect("userauths:sign-in")


def profile_update(request):
    profile = Profile.objects.get(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.user = request.user
            new_form.save()
            messages.success(request, "Profile Updated Successfully.")
            return redirect("core:dashboard")
    else:
        form = ProfileForm(instance=profile)

    context = {
        "form": form,
        "profile": profile,
    }

    return render(request, "userauths/profile-edit.html", context)