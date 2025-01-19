from utils.CustomPagination import CustomPagination
from django.http import JsonResponse
from rest_framework import viewsets, permissions
from .models import Pessoa, Relatorios, Digitador
from .serializers import (PessoaSerializer, RelatoriosSerializer,
                          DigitadorSerializer)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from utils.hash256 import hash256
from django.views.decorators.csrf import csrf_exempt
from utils.emitSocket import activate_table_trigger
from django.db.models import Q


def is_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True}, safe=False)
    else:
        return JsonResponse({'authenticated': False}, safe=False)


class DigitadorLoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        hashed_pass = hash256(password)
        user = authenticate(username=username, password=hashed_pass)

        if not user:
            raise AuthenticationFailed("Credenciais inválidas!")

        # Gera os tokens JWT
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


class EnablePartialUpdateMixin:
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class CleanQueryParamsMixin:
    """
    Mixin que limpa os parâmetros de consulta, removendo barras finais
    e aplicando lógica personalizada antes de processar os filtros.
    """

    def clean_query_params(self):
        """
        Limpa os parâmetros de consulta (query params), removendo barras finais.
        """
        query_params = self.request.query_params.dict()

        # Remove a barra final de cada valor
        for key in query_params.keys():
            if query_params[key]:
                query_params[key] = query_params[key].rstrip("/")

        return query_params


class PessoasAllViewSet(viewsets.ModelViewSet, EnablePartialUpdateMixin,
                        CleanQueryParamsMixin):
    allowed_methods = ["POST", "GET", "PUT",
                       "PATCH", "HEAD", "OPTIONS", "DELETE"]
    """
    API endpoint that allows users to be viewed or edited.
    """
    serializer_class = PessoaSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = "NIS_CPF"
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Sobrescreve o método get_queryset para aplicar filtros dinâmicos,
        incluindo lógica para campos booleanos.
        """
        queryset = Pessoa.objects.all().order_by("-created_at")
        filters = self.clean_query_params()  # Usa o mixin para limpar os query params

        # Remove parâmetros não relacionados a filtros
        filters.pop("page_size", None)

        # Construção de filtros dinâmicos
        query = Q()
        for key, value in filters.items():
            if value:

                # Tratamento especial para campos booleanos
                # Substitua por seus campos booleanos
                if key in ["isUnderInvestigation",]:
                    if value in ["0", "false"]:  # Se for falsy, filtra por False ou Null
                        query &= Q(**{f"{key}": False}) | Q(**
                                                            {f"{key}__isnull": True})
                    elif value in ["1", "true"]:  # Se for truthy, filtra por True
                        query &= Q(**{f"{key}": True})
                else:
                    # Filtro padrão para outros campos (insensível a maiúsculas)
                    query &= Q(**{f"{key}__icontains": value})

        return queryset.filter(query)

    """ def perform_create(self, serializer):
        instance = serializer.save()
        activate_table_trigger()
        return instance

    def perform_update(self, serializer):
        instance = serializer.save()
        activate_table_trigger()
        return instance

    def perform_destroy(self, instance):
        instance.delete()
        activate_table_trigger() """


class PessoasTodayViewSet(PessoasAllViewSet, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    def get_queryset(self):
        hoje = Pessoa.today()

        """
        Sobrescreve o método get_queryset para aplicar filtros dinâmicos,
        incluindo lógica para campos booleanos.
        """
        queryset = Pessoa.objects.filter(last_update=hoje).order_by("NdaFicha")
        filters = self.request.query_params.dict()

        # Remove parâmetros não relacionados a filtros
        filters.pop("page_size", None)

        # Construção de filtros dinâmicos
        query = Q()
        for key, value in filters.items():
            if value:

                # Tratamento especial para campos booleanos
                # Substitua por seus campos booleanos
                if key in ["isUnderInvestigation",]:
                    if value in ["0", "false"]:  # Se for falsy, filtra por False ou Null
                        query &= Q(**{f"{key}": False}) | Q(**
                                                            {f"{key}__isnull": True})
                    elif value in ["1", "true"]:  # Se for truthy, filtra por True
                        query &= Q(**{f"{key}": True})
                else:
                    # Filtro padrão para outros campos (insensível a maiúsculas)
                    query &= Q(**{f"{key}__icontains": value})

        return queryset.filter(query)


class RelatoriosViewSet(viewsets.ModelViewSet, CleanQueryParamsMixin):
    allowed_methods = ["GET", "HEAD", "OPTIONS"]  # Safe Methods only
    """
    API endpoint that allows users to just see data.
    """
    # queryset = Relatorios.objects.all().order_by('-data')
    serializer_class = RelatoriosSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        """
        Sobrescreve o método get_queryset para aplicar filtro.
        """
        queryset = Relatorios.objects.all().order_by('-data')
        filters = self.clean_query_params()  # Usa o mixin para limpar os query params
        data_param = filters.get("data")  # Obtém o parâmetro "data"

        if data_param:
            # Divide os períodos pelo separador ","
            periodos = data_param.split(",")

            # Inicializa uma consulta vazia usando Q
            query = Q()

            for periodo in periodos:
                try:
                    # Tente interpretar o período como ano e mês
                    ano, mes = periodo.split("-")
                    # Adiciona condições OR
                    query |= Q(data__year=int(ano), data__month=int(mes))
                except ValueError:
                    # Ignorar períodos inválidos
                    continue

            # Aplica o filtro baseado na consulta montada
            queryset = queryset.filter(query)

        return queryset


class DigitadorViewSet(viewsets.ModelViewSet):
    allowed_methods = ["POST", "GET", "PUT",
                       "PATCH", "HEAD", "OPTIONS", "DELETE"]
    queryset = Digitador.objects.all()
    serializer_class = DigitadorSerializer
    permission_classes = [permissions.IsAuthenticated]


def get_acoes(request):
    acoes = dict(Pessoa.AÇÕES)
    return JsonResponse(acoes, safe=False)


def get_prioridades(request):
    prioridades = dict(Pessoa.PRIORIDADES)
    return JsonResponse(prioridades, safe=False)


def get_status_choices(request):
    status_choices = dict(Pessoa.STATUS_CHOICES)
    return JsonResponse(status_choices, safe=False)


def get_doctypes(request):
    get_doctypes = dict(Pessoa.DOCTYPES)
    return JsonResponse(get_doctypes, safe=False)


def get_model(request):
    return JsonResponse(
        {"DocType": "DocType",
         "NdaFicha": "NdaFicha",
         "NIS_CPF": "NIS_CPF",
         "Nome": "Nome",
         "Endereço": "Endereço",
         "Ação": "Ação",
         "created_at": "created_at",
         "last_update": "last_update",
         "Prioridade": "Prioridade",
         "Status": "Status",
         "benefit_situation": 'benefit_situation'}
    )


def get_periods(request):
    # Obtém todos os registros do modelo Relatorio, ordenados por
    # 'id' em ordem decrescente
    relatorios = Relatorios.objects.all().order_by('-data')

    # Lista para armazenar os períodos únicos
    dates = []

    for relatorio in relatorios:
        # Obtém o id do registro
        date = str(relatorio.data)

        # Remove os últimos 3 caracteres do id
        final = date[:-3]

        # Adiciona o período se ainda não estiver na lista
        if final not in dates:
            dates.append(final)

    # Retorna os períodos como uma resposta JSON
    return JsonResponse(dates, safe=False)


def get_benefit_situations(request):
    benefitSituations = [
        'Bloqueado',
        'Cancelado',
        'Suspenso',
        'Liberado',
        'Não contemplado',
        'Desconhecido',
    ]

    return JsonResponse(benefitSituations, safe=False)


@csrf_exempt
def get_icon(request):
    try:
        name = request.GET.get('name')
        if not name:
            return JsonResponse(
                {"error": 'O parâmetro "name" é obrigatório.'},
                status=400
            )

        # Formata o nome para ser usado na URL (substituindo espaços por "+")
        formatted_name = name.strip().replace(" ", "+")
        print(formatted_name)

        # Gera a URL do avatar
        avatar_url = f"https://ui-avatars.com/api/?name={formatted_name}"

        # Retorna a URL do avatar
        return JsonResponse({"url": avatar_url})
    except Exception as e:
        print('Erro ao processar o pedido:', e)
        return JsonResponse(
            {"error": "Ocorreu um erro ao processar a solicitação."},
            status=500
        )
