from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    page_size = 10  # Número de itens por página
    page_size_query_param = 'page_size'
    max_page_size = 100  # Limite máximo de itens por página


class PessoaPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'pessoas_page_size'
    max_page_size = 100
