
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from .models import Acao, Perfil

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

    TIPO_CHOICES = [
        ('VOLUNTARIO', 'Ser Voluntário'),
        ('ORGANIZADOR', 'Ser Organizador'),
    ]
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_CHOICES, 
        widget=forms.RadioSelect,
        label="Eu quero:"
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'email', 'tipo_usuario', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Este email já está em uso.')
        return email


class SignInForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username', 'class': 'input-text'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Senha', 'class': 'input-text'}))


# Formulários para atualizar o perfil do usuário
class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'input-text'}),
            'last_name': forms.TextInput(attrs={'class': 'input-text'}),
            'email': forms.EmailInput(attrs={'class': 'input-text'}),
        }

class PerfilUpdateForm(forms.ModelForm):
    # Checkbox para multipla escolha de categorias
    preferencias = forms.MultipleChoiceField(
        choices=Acao.CATEGORIA_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Perfil
        fields = ['endereco', 'preferencias']
        widgets = {
            'endereco': forms.TextInput(attrs={'class': 'input-text', 'placeholder': 'Seu endereço completo'}),
        }
    
    # Lógica para carregar e salvar as categorias como string no banco
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.preferencias:
            self.initial['preferencias'] = self.instance.preferencias.split(',')

    def clean_preferencias(self):
        data = self.cleaned_data['preferencias']
        return ','.join(data) # Converte lista ['SAUDE', 'EDUCACAO'] para "SAUDE,EDUCACAO"