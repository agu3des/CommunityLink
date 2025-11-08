# Importe o modelo de User padrão do Django
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse

class Acao(models.Model):
    # Campos que você definiu
    titulo = models.CharField(max_length=200)
    descricao = models.TextField()
    data = models.DateTimeField() # Armazena data e hora
    local = models.CharField(max_length=255)
    numero_vagas = models.PositiveIntegerField()

    # Exemplo de categoria com 'choices'
    CATEGORIA_CHOICES = [
        ('SAUDE', 'Saúde'),
        ('EDUCACAO', 'Educação'),
        ('MEIO_AMBIENTE', 'Meio Ambiente'),
        ('ANIMAIS', 'Animais'),
        ('OUTRO', 'Outro'),
    ]
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, default='OUTRO')

    # --- Relacionamentos ---

    # 1. Organizador (Relação 1-para-N)
    organizador = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='acoes_criadas' # Assim, podemos fazer: user.acoes_criadas.all()
    )

    # 2. Voluntários (Relação N-para-N gerenciada pelo 'through')
    voluntarios = models.ManyToManyField(
        User,
        through='Inscricao',         # O nome do modelo intermediário
        related_name='acoes_inscritas', # Assim, podemos fazer: user.acoes_inscritas.all()
        blank=True                   # A ação pode começar sem nenhum voluntário
    )
    
    # --- Propriedades Úteis (Lógica no Modelo) ---
    
    @property
    def vagas_preenchidas(self):
        """ Retorna a contagem de voluntários ACEITOS. """
        return self.inscricao_set.filter(status='ACEITO').count()

    @property
    def esta_cheia(self):
        """ Retorna True se as vagas estiverem preenchidas, False caso contrário. """
        return self.vagas_preenchidas >= self.numero_vagas

    def __str__(self):
        return self.titulo
        
    def get_absolute_url(self):
        """ Retorna a URL para a página de detalhes desta ação. """
        return reverse('acao_detail', kwargs={'pk': self.pk})


class Inscricao(models.Model):
    """ Este modelo representa a 'solicitação' de um voluntário em uma ação. """
    
    STATUS_CHOICES = [
        ('PENDENTE', 'Pendente'),
        ('ACEITO', 'Aceito'),
        ('REJEITADO', 'Rejeitado'),
    ]

    # As duas 'pernas' da relação
    acao = models.ForeignKey(Acao, on_delete=models.CASCADE)
    voluntario = models.ForeignKey(User, on_delete=models.CASCADE)

    # O campo extra que justifica este modelo
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDENTE')
    
    # Data em que a solicitação foi feita
    data_inscricao = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Garante que um usuário não possa se inscrever 2x na mesma ação
        unique_together = ('acao', 'voluntario')

    def __str__(self):
        return f'{self.voluntario.username} em {self.acao.titulo} ({self.status})'


class Notificacao(models.Model):
    """ Modelo para notificações no sistema. """
    destinatario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensagem = models.CharField(max_length=255)
    lida = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # Link para onde a notificação deve levar ao ser clicada
    link = models.URLField(blank=True, null=True) 

    class Meta:
        ordering = ['-created_at'] # Mais recentes primeiro

    def __str__(self):
        return f"Notificação para {self.destinatario.username}: {self.mensagem[:30]}..."