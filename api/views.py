from django.http import JsonResponse
from rest_framework import viewsets, permissions
from rest_framework.exceptions import NotFound
from .models import Pessoa, Relatorios
from .serializers import PessoaSerializer, RelatoriosSerializer


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
