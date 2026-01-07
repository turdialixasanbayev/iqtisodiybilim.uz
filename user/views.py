from django.shortcuts import render, redirect
from django.views import View
from .tasks import send_notification_email_task
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import DeleteView, UpdateView, FormView
from django.contrib.auth import get_user_model
from .forms import ProfileUpdateForm, PasswordUpdateForm
import random
from django.core.files.base import ContentFile
from django.utils import timezone
import os, uuid
from django.core.files.storage import default_storage


def generate_otp_code():
    return str(random.randint(100000, 999999))


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
        profile_image_path = None
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

        if User.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered.")
            return redirect('register')
        
        if profile_image:
            ext = profile_image.name.split('.')[-1]
            filename = f"{uuid.uuid4()}.{ext}"
            path = os.path.join('temp', filename)
            saved_path = default_storage.save(path, profile_image)
            profile_image_path = saved_path

        otp_code = generate_otp_code()
        otp_created_at = timezone.now().timestamp()
        otp_last_sent = timezone.now().timestamp()

        request.session['register_data'] = {
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'bio': bio,
            'profile_image_path': profile_image_path,
            'otp_code': otp_code,
            'otp_created_at': otp_created_at,
            'otp_last_sent': otp_last_sent
        }

        send_notification_email_task.delay(
            subject="Email verification code",
            message=f"Your verification code: {otp_code}",
            to=email
        )

        messages.success(request, "Registration successful! A verification code has been sent to your email.")
        return redirect('verify')


class VerifyView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('register_data'):
            messages.error(request, "You need to register first before verifying your email.")
            return redirect('register')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'verify.html')

    def post(self, request):
        code = request.POST.get('code')
        register_data = request.session.get('register_data')

        if not register_data:
            messages.error(request, "No registration data found. Please register first.")
            return redirect('register')

        otp_created_at = register_data.get('otp_created_at')
        otp_code = register_data.get('otp_code')

        if timezone.now().timestamp() - otp_created_at > 300:
            messages.error(request, "This verification code has expired. Please request a new one.")
            return redirect('resend_otp')

        if code != otp_code:
            messages.error(request, "Invalid verification code. Please try again.")
            return redirect('verify')
        
        profile_image_path = register_data.get('profile_image_path')
        profile_image_file = None

        if profile_image_path:
            with default_storage.open(profile_image_path, 'rb') as f:
                profile_image_file = ContentFile(f.read(), name=os.path.basename(profile_image_path))

        user = User.objects.create_user(
            email=register_data.get('email'),
            password=register_data.get('password'),
            first_name=register_data.get('first_name'),
            last_name=register_data.get('last_name'),
            bio=register_data.get('bio'),
            profile_image=profile_image_file
        )

        login(request, user)

        send_notification_email_task.delay(
            subject="Email successfully verified 🎉",
            message=(
                f"Hello {user.first_name}!\n\n"
                "Your email address has been successfully verified.\n"
                "Your account is now active and you can log in.\n\n"
                "If this wasn't you, please contact our support immediately.\n\n"
                "Best regards,\n"
                "iqtisodiybilim.uz"
            ),
            to=user.email
        )

        messages.success(request, "Your email has been successfully verified! Welcome 🎉")

        del request.session['register_data']

        return redirect('dashboard')


class ResendOTPView(View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('register_data'):
            messages.error(request, "You need to register first before requesting a new code.")
            return redirect('register')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request):
        register_data = request.session.get('register_data')

        if not register_data:
            messages.error(request, "No registration data found. Please register first.")
            return redirect('register')

        email = register_data.get('email')
        last_sent = register_data.get('otp_last_sent')

        if last_sent and (timezone.now().timestamp() - last_sent < 60):
            messages.warning(request, "You can only resend the verification code once per minute. Please wait.")
            return redirect('verify')
        
        new_otp = generate_otp_code()

        register_data['otp_code'] = new_otp
        register_data['otp_created_at'] = timezone.now().timestamp()
        register_data['otp_last_sent'] = timezone.now().timestamp()
        request.session['register_data'] = register_data

        send_notification_email_task.delay(
            subject="Your new verification code",
            message=f"Your new verification code: {new_otp}",
            to=email
        )

        messages.success(request, "A new verification code has been sent to your email.")

        return redirect('verify')


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


class UpdateEmailView(LoginRequiredMixin, View):
    def get(self, request):
        return render(request, 'email_update.html')

    def post(self, request):
        new_email = request.POST.get('email')
        user = request.user

        if not new_email:
            messages.error(request, "Please enter a valid email.")
            return redirect('email-update')

        if User.objects.filter(email=new_email).exists():
            messages.error(request, "This email is already in use.")
            return redirect('email-update')
        
        otp_code = generate_otp_code()

        now_ts = timezone.now().timestamp()

        request.session['email_update_data'] = {
            'new_email': new_email,
            'otp_code': otp_code,
            'otp_created_at': now_ts,
            'otp_last_sent': now_ts,
            'old_email': user.email
        }

        send_notification_email_task.delay(
            subject="Confirm your new email",
            message=f"Your verification code: {otp_code}",
            to=new_email
        )

        messages.success(
            request,
            "A verification code has been sent to your new email address."
        )

        return redirect('verify-email-update')


class VerifyEmailUpdateView(LoginRequiredMixin, View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('email_update_data'):
            messages.error(request, "No email change request found.")
            return redirect('dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, 'verify_email_update.html')

    def post(self, request):
        code = request.POST.get('code')
        data = request.session.get('email_update_data')
        user = request.user

        if not data:
            messages.error(request, "No email change request found.")
            return redirect('dashboard')
        
        otp_code = data.get('otp_code')
        otp_created_at = data.get('otp_created_at')
        new_email = data.get('new_email')
        old_email = data.get('old_email')

        if timezone.now().timestamp() - otp_created_at > 300:
            messages.error(request, "Verification code expired. Please request a new one.")
            return redirect('resend-email-update-otp')

        if code != otp_code:
            messages.error(request, "Invalid verification code.")
            return redirect('verify-email-update')
        
        user.email = new_email
        user.save()

        send_notification_email_task.delay(
            subject="Your email was successfully updated",
            message=(
                f"Hello!\n\n"
                f"Your email address has been changed from {old_email} to {new_email}.\n"
                "If this wasn't you, please contact support immediately."
            ),
            to=old_email
        )

        del request.session['email_update_data']

        messages.success(request, "Your email has been successfully updated.")
        return redirect('dashboard')


class ResendEmailUpdateOTPView(LoginRequiredMixin, View):
    def post(self, request):
        data = request.session.get('email_update_data')
        now_ts = timezone.now().timestamp()

        if not data:
            messages.error(request, "No email change request found.")
            return redirect('dashboard')

        last_sent = data.get('otp_last_sent')

        if last_sent and (now_ts - last_sent < 60):
            messages.warning(request, "You can request a new code once per minute.")
            return redirect('verify-email-update')

        new_otp = generate_otp_code()

        data['otp_code'] = new_otp
        data['otp_created_at'] = now_ts
        data['otp_last_sent'] = now_ts

        request.session['email_update_data'] = data

        send_notification_email_task.delay(
            subject="Confirm your new email",
            message=f"Your new verification code: {new_otp}",
            to=data['new_email']
        )

        messages.success(request, "A new verification code has been sent.")

        return redirect('verify-email-update')
