from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

class UserRegistrationForm(UserCreationForm):
    # Username field: allow spaces, letters, numbers, and @/./+/-/_
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[RegexValidator(r'^[\w.@+\- ]+$', 'Enter a valid username. This value may contain letters, numbers, spaces, and @/./+/-/_ characters.')],
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username',
        }),
        help_text='Required. 150 characters or fewer. Spaces are allowed.'
    )
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}))
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].help_text = 'Your password must contain at least 8 characters.'
        self.fields['password2'].help_text = 'Enter the same password as before, for verification.'
        for field_name, field in self.fields.items():
            if field_name == 'username':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'Choose a username'})
            elif field_name == 'password1':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your password'})
            elif field_name == 'password2':
                field.widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm your password'})
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            username = username.strip()
        if User.objects.filter(username=username).exists():
            raise ValidationError('A user with that username already exists.')
        if len(username) > 150:
            raise ValidationError('Username must be 150 characters or fewer.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        # Remove the password similarity error if present
        password1 = cleaned_data.get('password1')
        username = cleaned_data.get('username')
        if password1 and username:
            errors = self._errors.get('password2')
            if errors:
                filtered = [e for e in errors if 'too similar' not in str(e)]
                if filtered:
                    self._errors['password2'] = filtered
                else:
                    del self._errors['password2']
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username'].strip()
        if commit:
            user.save()
        return user

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})) 