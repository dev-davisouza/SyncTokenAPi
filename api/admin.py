from django.contrib import admin
from .models import Pessoa
from django.contrib.auth.models import User


@admin.register(Pessoa)
class PessoaAdmin(admin.ModelAdmin):
    list_display = ['NIS_CPF', 'Nome', 'Endereço', 'Ação',
                    'created_at', 'last_update', 'Prioridade', 'Status']
    search_fields = ['Nome', 'NIS_CPF']


admin.register(User)
