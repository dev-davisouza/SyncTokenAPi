from django.db import models, transaction  # Importa o módulo de transações
from django.utils import timezone


class Pessoa (models.Model):
    AÇÕES = [
        ("Atualização cadastral", "Atualização cadastral"),
        ("Exclusão de pessoa", "Exclusão de pessoa"),
        ("Criação de cadastro", "Criação de cadastro"),
        ("Alteração de endereço", "Alteração de endereço"),
        ("Transferência", "Transferência"),
        ("Gestão de pessoa", "Gestão de pessoa"),
        ("Inclusão de pessoa", "Inclusão de pessoa"),
        ("Declaração escolar", "Declaração escolar"),
        ("Gestão de bloqueio/cancelamento", "Gestão de bloqueio/cancelamento"),
        ("Informarção de renda", "Informarção de renda"),
        ("Consulta", "Consulta"),

    ]

    AÇÕES.sort()

    PRIORIDADES = [
        ("Não", "Não"),
        ("Sim", "Sim")
    ]

    DOCTYPES = [
        ("CPF", "CPF"),
        ("NIS", "NIS")
    ]

    STATUS_CHOICES = [
        ("stts_0", "A ser atendido"),
        ("stts_1", "Em atendimento"),
        ("stts_2", "Atendimento encerrado"),
    ]

    DocType = models.CharField(
        "Tipo de documento", "DocType", choices=DOCTYPES, max_length=3,
        default="")
    NIS_CPF = models.CharField(
        "NIS ou CPF", "NIS_CPF", max_length=11, unique=True, primary_key=True)
    NdaFicha = models.IntegerField(
        "Número da Ficha", "NdaFicha", blank=True, null=True, default=0)
    Nome = models.CharField("Nome", "Nome", max_length=120)
    Endereço = models.TextField("Endereço", "Endereço")
    Ação = models.CharField("Ação", "Ação", choices=AÇÕES, max_length=50)
    created_at = models.DateField(auto_now_add=True, editable=False)
    last_update = models.DateField(auto_now=True, editable=True)
    Prioridade = models.CharField(
        "Prioridade", "Prioridade", choices=PRIORIDADES, max_length=3)
    Status = models.CharField(
        "Status", "Status", choices=STATUS_CHOICES, max_length=102)

    # Isso é usado la na view, n apague

    def today():
        return timezone.now().date()

    def save(self, *args, **kwargs):
        # Pegue a data de hoje baseado no fuso horário local
        today = timezone.now().date()

        # Use transações atômicas para evitar concorrência
        with transaction.atomic():
            # Conte quantas pessoas já compareceram hoje
            count_today = Pessoa.objects.filter(last_update=today).count()

            if self.pk:
                # Verifica se o objeto já existe e foi criado hoje
                try:
                    pessoa = Pessoa.objects.get(pk=self.pk)
                    if pessoa.created_at == today and pessoa.last_update == today:
                        pass
                    elif pessoa.last_update != today:
                        self.NdaFicha = count_today + 1
                except:
                    self.NdaFicha = count_today + 1
            else:
                self.NdaFicha = count_today + 1

        super().save(*args, **kwargs)  # Salva o objeto no banco de dados
        # Atualiza ou cria um relatório para o dia atual
        self.update_daily_report()

    def delete(self, *args, **kwargs):
        today = timezone.now().date()
        # Ao excluir uma pessoa, verifica se o relatório fica vazio
        relatorio = Relatorios.objects.filter(data=today).first()
        if relatorio:
            relatorio.pessoas.remove(self)
            relatorio.delete_if_empty()
        super().delete(*args, **kwargs)

    def update_daily_report(self):
        today = timezone.now().date()
        # Cria um novo relatório ou obtém o existente para o dia atual
        relatorio, is_created = Relatorios.objects.get_or_create(data=today)
        # Adiciona a pessoa ao relatório
        relatorio.pessoas.add(self)


class Relatorios (models.Model):
    data = models.DateField("data", "data", auto_now_add=True,
                            editable=False, primary_key=True)
    pessoas = models.ManyToManyField(Pessoa, related_name="relatorios")

    def __str__(self):
        return f"Relatório para {self.data}"

    def delete_if_empty(self):
        """Exclui o relatório se não houver pessoas associadas."""
        if self.pessoas.count() == 0:
            self.delete()
