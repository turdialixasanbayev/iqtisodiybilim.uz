from django.shortcuts import render, redirect

from django.views import View

from django.contrib.auth import login, logout, authenticate

from django.contrib.auth.mixins import LoginRequiredMixin

from django.contrib import messages

from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You're already logged in!")
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

        messages.success(request, "Registration and login successful! Welcome back.")
        return redirect('dashboard')


class LoginView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You're already logged in!")
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


class ProfileView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        return render(request, 'profile.html')


class LogoutView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        logout(request)
        messages.success(request, "You have successfully logged out.")
        return redirect('home')


class DeleteAccountView(LoginRequiredMixin, View):
    login_url = 'login'

    def get(self, request):
        user = request.user
        logout(request)
        user.delete()
        messages.success(request, "Your account has been deleted.")
        return redirect('home')
