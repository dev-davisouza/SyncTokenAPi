from django.test import TestCase
from api.models import Pessoa
from django.urls import reverse
from utils.cpf import generate_cpf


PESSOAS_ALL = 'pessoas-all-api-list'


class PaginationAPITest(TestCase):
    """
    O conteúdo gerado por qualquer uma das ViewSets deve ser obrigatoriamente
    um `JSON`. Nesta classe de testes usaremos uma base de dados local, o
    `db.sqlite3`, que será o nosso mock para testar a paginação.

    A paginação em si reorganizará o conteúdo desta ViewSet
    (`PessoasAllViewSet` e todos que herdam dela) sem causar adulteração nos
    dados. A questão aqui, é, que diferente do padrão gerado pela ViewSet, que
    entrega os dados de forma 'solta', aqui é esperado que o conteúdo seja
    dividido em 4 atributos:
    `count`, `next`, `previous` & `results`. Cada um deles possui
    responsabilidades distintas, mas que se complementam para formar uma
    paginação completa que seja aproveitável também no Front-end.

    `count` : É o somatório de todos os registros na base de dados daquela
        classe.

    `next` : Caso não retorne `null`, retorna a string do caminho para
        a próxima página. O `null` indica que não existe uma próxima página.

    `previous` : Caso não retorne `null`, retorna a string do caminho para
        a página anterior. O `null` indica que não existe uma página anterior.

    `results` : Encapsula os dados da consulta em um array de objetos
        `JavaScript`. Neste caso, cada objeto representa um registro da base.

    """

    def setUp(self):
        # Criando 50 objetos Pessoa para testar a paginação
        for i in range(50):
            if i < 10:
                Pessoa.objects.create(
                    NIS_CPF=generate_cpf(),
                    Nome=f'Pessoa 0{i}',
                    Endereço='Rua Teste, 123',
                    Ação='Criação de cadastro',
                    Prioridade='Não',
                    Status='stts_0'
                )
            else:
                Pessoa.objects.create(
                    NIS_CPF=generate_cpf(),
                    Nome=f'Pessoa {i}',
                    Endereço='Rua Teste, 123',
                    Ação='Criação de cadastro',
                    Prioridade='Não',
                    Status='stts_0'
                )

    def test_pagination_ok(self):
        # Fazendo uma requisição GET à sua ViewSet
        # Altere 'pessoas-list' para o nome correto da URL
        url = reverse(PESSOAS_ALL)
        response = self.client.get(url)

        # Verificando se o status da resposta é 200 OK
        self.assertEqual(response.status_code, 200)

    def test_pagination_generate_next(self):
        url = reverse(PESSOAS_ALL)
        response = self.client.get(url)

        # Pega o attr 'content'
        res_content = str(response.content)

        # Testa se o attr 'next' está no conteúdo da requisição
        self.assertIn("next", res_content)

    def test_pagination_generate_count(self):
        url = reverse(PESSOAS_ALL)
        response = self.client.get(url)

        # pega o attr 'content'
        res_content = str(response.content)

        # Testa se o attr 'count' está no conteúdo da requisição
        self.assertIn('count', res_content)

    def test_pagination_generate_previous(self):
        url = reverse(PESSOAS_ALL)
        response = self.client.get(url)

        # pega o attr 'content'
        res_content = str(response.content)

        # Testa se o attr 'previous' está no conteúdo da requisição
        self.assertIn('previous', res_content)

    def test_pagination_generate_results(self):
        url = reverse(PESSOAS_ALL)
        response = self.client.get(url)

        # pega o attr 'content'
        res_content = str(response.content)

        # Testa se o attr 'results' está no conteúdo da requisição
        self.assertIn('results', res_content)

    def test_pagination_results_attr_no_content(self):
        # Deletando todos os dados gerados no setUp
        Pessoa.objects.all().delete()

        url = reverse(PESSOAS_ALL)
        response = self.client.get(url)

        # Converte em JSON
        response = response.json()

        # pega o valor do attr 'content'
        res_content = response['results']

        # Testa se o campo 'results' retornou um array vazio
        self.assertEqual(res_content, [])
