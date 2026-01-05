from django.shortcuts import render, redirect
from django.views import View
from .models import CustomUser, EmailOTP
from .tasks import send_notification_email_task
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.utils import timezone

class RegisterView(View):
    def get(self, request):
        return render(request, 'register.html')
    
    def post(self, request):
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        bio = request.POST.get('bio')
        profile_image = request.FILES.get('profile_image')
        email = request.POST.get('email')
        password = request.POST.get('password')
        repeat_password = request.POST.get('repeat_password')

        if not all([email, password, repeat_password]):
            return redirect('register')
        if password != repeat_password:
            return redirect('register')
        if len(password) < 8:
            return redirect('register')
        if CustomUser.objects.filter(email=email).exists():
            return redirect('register')
        
        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            bio=bio,
            profile_image=profile_image,
            is_active=False
        )

        code = EmailOTP.generate()
        EmailOTP.objects.create(user=user, code=code)

        send_notification_email_task.delay(
            subject="Email verification code",
            message=f"Your verification code: {code}",
            to=email
        )

        request.session['verify_user_id'] = user.id

        return redirect('verify')


class VerifyView(View):
    def get(self, request):
        return render(request, 'verify.html')

    def post(self, request):
        code = request.POST.get('code')
        user_id = request.session.get('verify_user_id')

        if not user_id:
            return redirect('register')

        try:
            otp = EmailOTP.objects.get(
                user_id=user_id,
                code=code,
                is_used=False
            )
        except EmailOTP.DoesNotExist:
            return redirect('verify')

        if otp.is_expired():
            return redirect('verify')

        otp.is_used = True
        otp.save()

        user = otp.user
        user.is_active = True
        user.save()

        login(request, user)
        send_notification_email_task.delay(
            subject="Email successfully verified 🎉",
            message=(
                "Hello!\n\n"
                "Your email address has been successfully verified.\n"
                "Your account is now active and you can log in.\n\n"
                "If this wasn't you, please contact our support immediately.\n\n"
                "Best regards,\n"
                "iqtisodiybilim.uz"
            ),
            to=user.email
        )
        del request.session['verify_user_id']

        return redirect('dashboard')

class ProfileView(View):
    def get(self, request):
        return render(request, 'profile.html')


class LogoutView(LoginRequiredMixin, View):
    login_url = 'login'
    redirect_field_name = None

    def get(self, request, *args, **kwargs):
        logout(request)
        request.session.flush()
        return redirect('home')


class LoginView(View):
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return redirect('login')


class ResendOTPView(View):
    def post(self, request):
        user_id = request.session.get('verify_user_id')

        if not user_id:
            return redirect('register')

        user = CustomUser.objects.get(id=user_id)

        cache_key = f"otp_resend_{user.id}"

        if cache.get(cache_key):
            return redirect('verify')

        EmailOTP.objects.filter(user=user).delete()

        code = EmailOTP.generate()
        EmailOTP.objects.create(user=user, code=code)

        send_notification_email_task.delay(
            subject="Email verification code",
            message=f"Your new verification code: {code}",
            to=user.email
        )

        cache.set(cache_key, True, timeout=60)

        return redirect('verify')
