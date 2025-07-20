# app/forms.py
from django import forms
from .models import Thread, User

class ThreadForm(forms.ModelForm):
    class Meta:
        model = Thread
        fields = ['thread_name', 'slug', 'password']  # 'title' を 'thread_name' に変更
        widgets = {
            'thread_name': forms.TextInput(attrs={'placeholder': 'スレッドの名前を入力'}),
            'slug': forms.TextInput(attrs={'placeholder': 'スレッドのスラッグを入力'}),
            'password': forms.TextInput(attrs={'placeholder': 'スレッドのパスを入力'}),
        }

class UserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Password (confirm)")

    class Meta:
        model = User
        fields = ['username', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Passwords don't match")
        return cleaned_data

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        if not any(char.isdigit() for char in password):
            raise forms.ValidationError("Password must contain at least one digit.")
        if not any(char.isupper() for char in password):
            raise forms.ValidationError("Password must contain at least one uppercase letter.")
        if not any(char.islower() for char in password):
            raise forms.ValidationError("Password must contain at least one lowercase letter.")
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
            raise forms.ValidationError("Password must contain at least one special character.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
