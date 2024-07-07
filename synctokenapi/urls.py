from django.urls import include, path
from rest_framework import routers
from api.views import get_acoes, get_prioridades, get_status_choices, get_doctypes
from api import views


router = routers.DefaultRouter()
router.register(r'pessoas', views.PessoasTodayViewSet, basename="pessoas-api")
router.register(r'pessoas-all', views.PessoasAllViewSet,
                basename="pessoas-all-api")
router.register(r'relatorios', views.RelatoriosViewSet,
                basename="relatorios-api")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include(
        'rest_framework.urls', namespace='rest_framework')),
    path('acoes/', get_acoes, name='get_acoes'),
    path('prioridades/', get_prioridades, name='get_prioridades'),
    path('status_choices/', get_status_choices, name='get_status_choices'),
    path('doctypes/', get_doctypes, name='get_doctypes'),
]
