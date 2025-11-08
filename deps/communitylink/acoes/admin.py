from django.contrib import admin
from .models import Acao, Inscricao, Notificacao

# Classe para mostrar Inscrições "inline" (dentro da página da Ação)
class InscricaoInline(admin.TabularInline):
    model = Inscricao
    extra = 1 # Quantos campos vazios mostrar

@admin.register(Acao)
class AcaoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'organizador', 'data', 'local', 'numero_vagas', 'esta_cheia')
    list_filter = ('categoria', 'data', 'organizador')
    search_fields = ('titulo', 'descricao')
    inlines = [InscricaoInline] # Adiciona o inline

@admin.register(Inscricao)
class InscricaoAdmin(admin.ModelAdmin):
    list_display = ('acao', 'voluntario', 'status', 'data_inscricao')
    list_filter = ('status', 'acao')
    search_fields = ('voluntario__username', 'acao__titulo')

# Registra Notificacao
@admin.register(Notificacao)
class NotificacaoAdmin(admin.ModelAdmin):
    list_display = ('destinatario', 'mensagem', 'lida', 'created_at')
    list_filter = ('lida', 'created_at')