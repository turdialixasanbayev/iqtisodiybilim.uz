from django.shortcuts import render, redirect
from django.views import View
from .models import CustomUser, EmailOTP
from .tasks import send_notification_email_task
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView, FormView
from django.contrib.auth import get_user_model
from .forms import ProfileUpdateForm, PasswordUpdateForm

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
        email = request.POST.get('email')
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
        
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
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

        messages.success(request, "Registration successful! A verification code has been sent to your email.")
        return redirect('verify')


class VerifyView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('verify_user_id'):
            messages.error(request, "You need to register first before verifying your email.")
            return redirect('register')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'verify.html')

    def post(self, request):
        code = request.POST.get('code')
        user_id = request.session.get('verify_user_id')

        if not user_id:
            messages.error(request, "No user to verify. Please register first.")
            return redirect('register')

        try:
            otp = EmailOTP.objects.get(
                user_id=user_id,
                code=code,
                is_used=False
            )
        except EmailOTP.DoesNotExist:
            messages.error(request, "Invalid verification code. Please try again.")
            return redirect('verify')

        if otp.is_expired():
            messages.error(request, "This verification code has expired. A new code has been sent to your email.")
            user = otp.user
            EmailOTP.objects.filter(user=user).delete()
            new_code = EmailOTP.generate()
            EmailOTP.objects.create(user=user, code=new_code)
            send_notification_email_task.delay(
                subject="New verification code",
                message=f"Your new verification code: {new_code}",
                to=user.email
            )
            return redirect('verify')

        otp.is_used = True
        otp.save()

        user = otp.user
        user.is_active = True
        user.save()

        login(request, user)
        messages.success(request, "Your email has been successfully verified! Welcome 🎉")

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
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.info(request, "You are already logged in!")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful! Welcome back.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid email or password. Please try again.")
            return redirect('login')


class ResendOTPView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('verify_user_id'):
            messages.error(request, "You need to register first before requesting a new code.")
            return redirect('register')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        user_id = request.session.get('verify_user_id')

        if not user_id:
            messages.error(request, "No user to resend OTP for. Please register first.")
            return redirect('register')

        user = CustomUser.objects.get(id=user_id)
        cache_key = f"otp_resend_{user.id}"

        if cache.get(cache_key):
            messages.warning(request, "You can only resend the verification code once per minute. Please wait.")
            return redirect('verify')

        # Delete old OTPs and create a new one
        EmailOTP.objects.filter(user=user).delete()
        code = EmailOTP.generate()
        EmailOTP.objects.create(user=user, code=code)

        send_notification_email_task.delay(
            subject="Email verification code",
            message=f"Your new verification code: {code}",
            to=user.email
        )

        # Limit resend to once per minute
        cache.set(cache_key, True, timeout=60)

        messages.success(request, "A new verification code has been sent to your email.")
        return redirect('verify')


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


class UpdateEmailView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'email_update.html')

    def post(self, request):
        new_email = request.POST.get('email')

        if not new_email:
            messages.error(request, "Please enter a valid email.")
            return redirect('email-update')

        if CustomUser.objects.filter(email=new_email).exists():
            messages.error(request, "This email is already in use.")
            return redirect('email-update')

        user = request.user
        user.pending_email = new_email
        user.save()

        EmailOTP.objects.filter(user=user).delete()

        code = EmailOTP.generate()
        EmailOTP.objects.create(user=user, code=code)

        send_notification_email_task.delay(
            subject="Confirm your new email",
            message=f"Your verification code: {code}",
            to=new_email
        )

        request.session['verify_email_change'] = True

        messages.success(
            request,
            "A verification code has been sent to your new email address."
        )
        return redirect('verify-email-update')


class VerifyEmailUpdateView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('verify_email_change'):
            messages.error(request, "No email change request found.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'verify_email_update.html')

    def post(self, request):
        code = request.POST.get('code')
        user = request.user

        try:
            otp = EmailOTP.objects.get(
                user=user,
                code=code,
                is_used=False
            )
        except EmailOTP.DoesNotExist:
            messages.error(request, "Invalid verification code.")
            return redirect('verify-email-update')

        if otp.is_expired():
            messages.error(
                request,
                "Verification code expired. A new code has been sent."
            )
            EmailOTP.objects.filter(user=user).delete()

            new_code = EmailOTP.generate()
            EmailOTP.objects.create(user=user, code=new_code)

            send_notification_email_task.delay(
                subject="New email verification code",
                message=f"Your new code: {new_code}",
                to=user.pending_email
            )
            return redirect('verify-email-update')

        otp.is_used = True
        otp.save()

        user.email = user.pending_email
        user.pending_email = None
        user.save()

        del request.session['verify_email_change']

        messages.success(request, "Your email has been successfully updated.")
        return redirect('dashboard')


class ResendEmailUpdateOTPView(LoginRequiredMixin, View):
    def post(self, request):
        user = request.user
        cache_key = f"email_update_otp_{user.id}"

        if cache.get(cache_key):
            messages.warning(
                request,
                "You can request a new code once per minute."
            )
            return redirect('verify-email-update')

        EmailOTP.objects.filter(user=user).delete()
        code = EmailOTP.generate()
        EmailOTP.objects.create(user=user, code=code)

        send_notification_email_task.delay(
            subject="Confirm your new email",
            message=f"Your new verification code: {code}",
            to=user.pending_email
        )

        cache.set(cache_key, True, timeout=60)

        messages.success(
            request,
            "A new verification code has been sent."
        )
        return redirect('verify-email-update')
