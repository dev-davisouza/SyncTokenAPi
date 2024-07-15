from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.decorators import api_view
from .models import Pessoa, Relatorios
from .serializers import PessoaSerializer, RelatoriosSerializer
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken


def is_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True}, safe=False)
    else:
        return JsonResponse({'authenticated': False}, safe=False)


@api_view(['POST'])
def login_user(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        refresh = RefreshToken.for_user(user)
        return JsonResponse({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }, safe=False)
    else:
        return JsonResponse({'detail': "Credenciais não conferem!"},
                            safe=False, status=401)


class EnablePartialUpdateMixin:

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class PessoasAllViewSet(viewsets.ModelViewSet, EnablePartialUpdateMixin):
    allowed_methods = ["POST", "GET", "PUT",
                       "PATCH", "HEAD", "OPTIONS", "DELETE"]
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Pessoa.objects.all().order_by("Nome")
    serializer_class = PessoaSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "NIS_CPF"


class PessoasTodayViewSet(PessoasAllViewSet, viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    hoje = Pessoa.today()
    queryset = Pessoa.objects.filter(last_update=hoje).order_by("NdaFicha")


class RelatoriosViewSet(viewsets.ModelViewSet):
    allowed_methods = ["GET", "HEAD", "OPTIONS"]  # Safe Methods only
    """
    API endpoint that allows users to just see data.
    """
    # Prefetch dados de Pessoa relacionados e filtra relatórios do dia atual
    queryset = Relatorios.objects.all()
    serializer_class = RelatoriosSerializer
    permission_classes = [permissions.AllowAny]


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
