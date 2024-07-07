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
        is_new = not Pessoa.objects.filter(pk=self.pk).exists()
        if is_new:
            with transaction.atomic():
                today = timezone.now().date()
                count_today = Pessoa.objects.filter(
                    created_at=today).count()
                self.NdaFicha = count_today + 1
                print(
                    f"Debug: NdaFicha set to {self.NdaFicha} for date {today}")
        super().save(*args, **kwargs)  # Salva o objeto no banco de dados
        # Atualiza ou cria um relatório para o dia atual
        self.update_daily_report()

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
