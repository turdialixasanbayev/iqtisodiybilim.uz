from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError


User = get_user_model()

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'bio', 'profile_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.required = False


class PasswordUpdateForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Current password"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="New password",
        min_length=8
    )
    repeat_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Repeat new password"
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password")

        if not self.user.check_password(current):
            raise ValidationError("Current password is incorrect.")

        return current

    def clean(self):
        cleaned_data = super().clean()

        new_password = cleaned_data.get("new_password")
        repeat_password = cleaned_data.get("repeat_password")

        if new_password and repeat_password:
            if new_password != repeat_password:
                raise ValidationError("New passwords do not match.")

            if len(new_password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")

        return cleaned_data
