
from django import forms
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
