from django.http import JsonResponse
from rest_framework import viewsets, permissions
from .models import Pessoa, Relatorios
from .serializers import PessoaSerializer, RelatoriosSerializer
from utils.CustomPagination import CustomPagination
#  from rest_framework.response import Response


def is_auth(request):
    if request.user.is_authenticated:
        return JsonResponse({'authenticated': True}, safe=False)
    else:
        return JsonResponse({'authenticated': False}, safe=False)


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
    queryset = Pessoa.objects.all().order_by("-created_at")
    serializer_class = PessoaSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "NIS_CPF"
    pagination_class = CustomPagination


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
    queryset = Relatorios.objects.all().order_by('-data')
    serializer_class = RelatoriosSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPagination


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
         "Status": "Status"}
    )
