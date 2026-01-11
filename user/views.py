from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView, FormView
from django.contrib.auth import get_user_model
from .forms import ProfileUpdateForm, PasswordUpdateForm
import random
from django.utils import timezone


# def generate_otp_code():
#     return str(random.randint(100000, 999999))


User = get_user_model()


class RegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        profile_image = request.FILES.get('profile_image')
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')

        if not all([email, password, repeat_password]):
            messages.error(request, "Please fill in all required fields.")
            return redirect('register')

        if password != repeat_password:
            messages.error(request, "Passwords do not match.")
            return redirect('register')

        if len(password) < 8:
            messages.error(request, "Password must be at least 8 characters long.")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('register')
        
        user = User.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            profile_image=profile_image
        )

        login(request, user)

        messages.success(request, "Registration successful!")
        return redirect('dashboard')


class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        email = request.POST.get('email').strip().lower()
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful! Welcome back.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('login')


class ProfileView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.info(request, "You are not log in!")
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'profile.html')


class LogoutView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = None

    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.flush()
        messages.success(request, "You have successfully logged out.")
        return redirect('home')


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'delete_account.html'
    success_url = reverse_lazy('home')
    context_object_name = 'user'

    def get_object(self, queryset=None):
        return self.request.user


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    form_class = ProfileUpdateForm
    template_name = 'profile_update.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        return self.request.user


class PasswordUpdateView(LoginRequiredMixin, FormView):
    template_name = "password_update.html"
    form_class = PasswordUpdateForm
    success_url = reverse_lazy("dashboard")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = self.request.user
        user.set_password(form.cleaned_data["new_password"])
        user.save()

        update_session_auth_hash(self.request, user)

        return super().form_valid(form)
