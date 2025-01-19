from django.contrib.auth.models import User
from django.db import models, transaction  # Importa o módulo de transações
from django.utils import timezone
from utils.hash256 import hash256


class Pessoa (models.Model):
    AÇÕES = [
        ("Atualização cadastral", "Atualização cadastral"),
        ("Exclusão de pessoa", "Exclusão de pessoa"),
        ("Exclusão e Inclusão de pessoa", "Exclusão e Inclusão de pessoa"),
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

    benefitSituations = [
        ('Bloqueado', 'Bloqueado'),
        ('Cancelado', 'Cancelado'),
        ('Suspenso', 'Suspenso'),
        ('Liberado', 'Liberado'),
        ('Não contemplado', 'Não contemplado'),
        ('Desconhecido', 'Desconhecido'),
    ]

    DocType = models.CharField(
        "Tipo de documento", "DocType", choices=DOCTYPES, max_length=3,
        default="")

    NdaFicha = models.IntegerField(
        "Número da Ficha", "NdaFicha", blank=True, null=True, default=0)

    NIS_CPF = models.CharField(
        "NIS ou CPF", "NIS_CPF", max_length=11, unique=True, primary_key=True)

    Nome = models.CharField("Nome", "Nome", max_length=120)

    Endereço = models.TextField("Endereço", "Endereço")

    Ação = models.CharField("Ação", "Ação", choices=AÇÕES, max_length=50)

    created_at = models.DateField(auto_now_add=True, editable=False)

    last_update = models.DateField(auto_now=True, editable=True)

    Prioridade = models.CharField(
        "Prioridade", "Prioridade", choices=PRIORIDADES, max_length=3)

    Status = models.CharField(
        "Status", "Status", choices=STATUS_CHOICES, max_length=102)

    benefit_situation = models.CharField(
        "benefit_situation", "benefit_situation", choices=benefitSituations,
        max_length=15, default="Desconhecido", null=True, blank=True)

    isUnderInvestigation = models.BooleanField(
        "isUnderInvestigation", "isUnderInvestigation", null=True, blank=True, default=False)

    # Isso é usado la na view, n apague
    @staticmethod
    def today():
        return timezone.localdate()

    def save(self, *args, **kwargs):
        # Pegue a data de hoje baseado no fuso horário local
        today = timezone.localdate()

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
        Relatorios.delete_all_empty()
        self.update_daily_report()

    def delete(self, *args, **kwargs):
        today = timezone.localdate()
        # Ao excluir uma pessoa, verifica se o relatório fica vazio
        relatorio = Relatorios.objects.filter(data=today).first()
        if relatorio:
            relatorio.pessoas.remove(self)
            relatorio.delete_if_empty()
        super().delete(*args, **kwargs)
        Relatorios.delete_all_empty()
        Pessoa.recalculate_ndaficha()

    def update_daily_report(self):
        today = timezone.localdate()  # Obtém a data de hoje

        # Use transações atômicas para evitar problemas de concorrência
        with transaction.atomic():
            # Cria um novo relatório ou obtém o existente para o dia atual
            relatorio, created = Relatorios.objects.get_or_create(data=today)

            if not created:
                # Se o relatório já existe e foi criado, ele pode ser atualizado conforme necessário
                # Adicione a pessoa ao relatório
                if not self in relatorio.pessoas.all():
                    relatorio.pessoas.add(self)
            else:
                # Se o relatório foi recém-criado, adicione a pessoa
                relatorio.pessoas.add(self)

            # Salve o relatório atualizado
            relatorio.save()

    def recalculate_ndaficha():
        today = timezone.localdate()
        pessoas = Pessoa.objects.filter(
            last_update=today).order_by('NdaFicha')

        # Recalcula os valores de NdaFicha
        for index, pessoa in enumerate(pessoas, start=1):
            pessoa.NdaFicha = index
            pessoa.save(update_fields=['NdaFicha'])


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

    @classmethod
    def delete_all_empty(cls):
        """Exclui todos os relatórios sem pessoas associadas."""
        empty_reports = cls.objects.annotate(
            num_pessoas=models.Count('pessoas')).filter(num_pessoas=0)
        empty_reports.delete()


class Digitador(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, verbose_name="user",
        name="user", blank=True)
    username = models.CharField("username", "username", primary_key=True,
                                unique=True, null=False, blank=False,
                                max_length=15)
    # Armazena o hash SHA-256 da senha
    password = models.CharField(max_length=64, blank=False,
                                null=False,
                                help_text="A senha é obrigatória.")

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para garantir
        que o User seja criado automaticamente e
        a senha seja armazenada como hash.
        """
        # Cria um User correspondente
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
        # Atualiza a senha do User, se necessário
        self.user.save()

        # Garante que a senha do Digitador esteja em formato de hash
        super().save(*args, **kwargs)

    def passwords_match(self, password: str) -> bool:
        """
        Compara a senha fornecida com a senha atual armazenada no modelo.
        :param password: Senha em texto puro fornecida para comparação.
        :return: True se as senhas coincidirem, False caso contrário.
        """
        return hash256(password) == self.password

    @classmethod
    def authenticate(cls, user: str, password: str) -> bool:
        """
        Valida a existência de um usuário pelas credenciais de acesso.
        :param user: Nome de usuário.
        :param password: Senha em texto puro.
        :return: True se as credenciais forem válidas, False caso contrário.
        """
        try:
            digitador = cls.objects.get(user=user)
            return digitador.passwords_match(password)
        except cls.DoesNotExist:
            return False
