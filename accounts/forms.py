from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from accounts.models import Wallet


class UserCreateForm(UserCreationForm):
    class Meta:
        fields = ('username', 'email', 'password1', 'password2')
        model = get_user_model()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Display name'
        self.fields['email'].label = 'Email address'

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            Wallet.objects.create(user=user)
        return user
