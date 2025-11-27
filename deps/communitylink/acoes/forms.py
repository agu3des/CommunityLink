
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Acao

class AcaoForm(forms.ModelForm):
    # Configura o campo 'data' para usar um widget de data/hora bonitinho
    data = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        input_formats=['%Y-%m-%dT%H:%M']
    )

    class Meta:
        model = Acao
        # Campos que o *usuário* deve preencher
        fields = ['titulo', 'descricao', 'data', 'local', 'categoria', 'numero_vagas']
        # O 'organizador' será definido automaticamente na view
        # Os 'voluntarios' serão gerenciados pelas inscrições


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'placeholder': 'email@exemplo.com', 'class': 'input-text'}))

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este email já está em uso.')
        return email


class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'input-text'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Senha', 'class': 'input-text'}))