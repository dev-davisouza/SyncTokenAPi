from django.test import TestCase, Client
from rest_framework import status
from datetime import date
from api.models import Pessoa, Relatorios


class PessoasAPI(TestCase):

    def setUp(self):
        """Configura o cliente e o URL para os testes."""
        self.client = Client()

        # Endpoint da API
        self.url = 'http://127.0.0.1:8000/pessoas-all/'

        # Mock
        self.data = {
            'DocType': "CPF",
            'NIS_CPF': '98765432100',
            'Nome': 'Maria Oliveira',
            'Endereço': 'Rua Teste, 456',
            'Ação': 'Criação de cadastro',
            'Prioridade': 'Não',
            'Status': 'stts_0'
        }

    def test_post_data_is_ok(self):
        """Teste o envio de dados para a API e verifica a resposta."""

        # Envia uma requisição POST para o endpoint da API
        response = self.client.post(
            self.url, self.data, content_type='application/json')

        # Verifica se a resposta tem o status code 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica se a resposta contém os dados enviados
        self.assertEqual(response.data['NIS_CPF'], self.data['NIS_CPF'])
        self.assertEqual(response.data['Nome'], self.data['Nome'])
        self.assertEqual(response.data['Endereço'], self.data['Endereço'])
        self.assertEqual(response.data['Ação'], self.data['Ação'])
        self.assertEqual(response.data['Prioridade'], self.data['Prioridade'])
        self.assertEqual(response.data['Status'], self.data['Status'])

    def test_put_data_is_ok(self):
        # Crie um objeto mockado
        self.client.post(
            self.url, self.data, content_type='application/json')

        # altere os dados
        data = self.data
        data['Status'] = 'stts_2'

        # Pegue o ID e procure na base de dados
        id = self.data['NIS_CPF']

        # Combine o caminho da URL com o parâmetro de busca
        url = f'{self.url}{id}/'

        request = self.client.put(
            url, data, content_type='application/json')

        self.assertEqual(request.status_code, status.HTTP_200_OK)

    def test_relatorio_is_created(self):
        """Teste se um Relatorio é criado e a nova Pessoa é
            adicionada ao Relatorio"""
        # Dados válidos para criar uma nova pessoa

        # Envia uma requisição POST para o endpoint da API
        response = self.client.post(
            self.url, self.data, content_type='application/json'
        )

        # Verifica se a resposta tem o status code 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Obtém o relatório para hoje
        today = date.today()
        relatorio = Relatorios.objects.get(data=today)

        # Verifica se a Pessoa foi adicionada ao Relatorio
        self.assertIn(Pessoa.objects.get(
            NIS_CPF=self.data['NIS_CPF']), relatorio.pessoas.all())
        # Verifica que a contagem é 1
        self.assertEqual(relatorio.pessoas.count(), 1)

    def test_relatorio_can_do_self_delete(self):
        """Teste se o relatório deleta a si mesmo caso
        todas as pessoas tenham sido excluídas"""

        # Envia uma requisição POST para o endpoint da API
        response = self.client.post(
            self.url, self.data, content_type='application/json'
        )

        # Verifica se a resposta tem o status code 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Obtém o relatório para hoje
        today = date.today()
        # relatorio = Relatorios.objects.get(data=today)

        # Pega a pessoa que foi criada
        pessoa = Pessoa.objects.get(NIS_CPF=self.data['NIS_CPF'])

        # Força a exclusão do objeto de pessoa
        pessoa.delete()

        # Após excluir a pessoa, verificamos se o relatório foi excluído
        with self.assertRaises(Relatorios.DoesNotExist):
            Relatorios.objects.get(data=today)
