from django.urls import include, path
from rest_framework import routers
from api.views import (get_acoes, get_prioridades,
                       get_status_choices, get_doctypes, get_model, is_auth)
from api import views
from django.contrib import admin
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)


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
    path('admin/', admin.site.urls),
    path('api-auth/', include(
        'rest_framework.urls', namespace='rest_framework')),
    path('acoes/', get_acoes, name='get_acoes'),
    path('prioridades/', get_prioridades, name='get_prioridades'),
    path('status_choices/', get_status_choices, name='get_status_choices'),
    path('doctypes/', get_doctypes, name='get_doctypes'),
    path('model/', get_model, name='get_model'),
    path('is-auth/', is_auth, name='get_is-auth'),
    path('api/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]
