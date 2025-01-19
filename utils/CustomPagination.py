from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100  # Limite máximo de itens por página

    def paginate_queryset(self, queryset, request, view=None):
        # Limpa o parâmetro `page_size` diretamente
        if self.page_size_query_param in request.query_params:
            page_size = request.query_params.get(
                self.page_size_query_param, "").rstrip("/")
            # Atualiza o parâmetro para garantir que seja válido
            if page_size.isdigit():
                self.page_size = int(page_size)

        return super().paginate_queryset(queryset, request, view)


class PessoaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pessoas_page_size'
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        # Limpa o parâmetro `pessoas_page_size` diretamente
        if self.page_size_query_param in request.query_params:
            pessoas_page_size = request.query_params.get(
                self.page_size_query_param, "").rstrip("/")
            # Atualiza o parâmetro para garantir que seja válido
            if pessoas_page_size.isdigit():
                self.page_size = int(pessoas_page_size)

        return super().paginate_queryset(queryset, request, view)
