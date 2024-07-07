from django.test import TestCase, Client
from rest_framework import status
from datetime import date
from api.models import Pessoa, Relatorios


class PessoasAPI(TestCase):
    def setUp(self):
        """Configura o cliente e o URL para os testes."""
        self.client = Client()
        # Substitua pelo endpoint correto da sua API
        self.url = 'http://127.0.0.1:8000/pessoas/'

    def test_post_data_is_ok(self):
        """Teste o envio de dados para a API e verifica a resposta."""
        # Dados válidos para criar uma nova pessoa
        data = {
            'NIS_CPF': '12345678901',
            'Nome': 'João Silva',
            'Endereço': 'Rua Teste, 123',
            'Ação': 'Atualização cadastral',
            'Prioridade': 'Sim',
            'Status': 'stts_0'
        }

        # Envia uma requisição POST para o endpoint da API
        response = self.client.post(
            self.url, data, content_type='application/json')

        # Verifica se a resposta tem o status code 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verifica se a resposta contém os dados enviados
        self.assertEqual(response.data['NIS_CPF'], data['NIS_CPF'])
        self.assertEqual(response.data['Nome'], data['Nome'])
        self.assertEqual(response.data['Endereço'], data['Endereço'])
        self.assertEqual(response.data['Ação'], data['Ação'])
        self.assertEqual(response.data['Prioridade'], data['Prioridade'])
        self.assertEqual(response.data['Status'], data['Status'])

    def test_relatorio_is_created(self):
        """Teste se um Relatorio é criado e a nova Pessoa é
            adicionada ao Relatorio"""
        # Dados válidos para criar uma nova pessoa
        data = {
            'NIS_CPF': '98765432100',
            'Nome': 'Maria Oliveira',
            'Endereço': 'Rua Teste, 456',
            'Ação': 'Criação de cadastro',
            'Prioridade': 'Não',
            'Status': 'stts_0'
        }

        # Envia uma requisição POST para o endpoint da API
        response = self.client.post(
            self.url, data, content_type='application/json'
        )

        # Verifica se a resposta tem o status code 201 Created
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Obtém o relatório para hoje
        today = date.today()
        relatorio = Relatorios.objects.get(data=today)

        # Verifica se a Pessoa foi adicionada ao Relatorio
        self.assertIn(Pessoa.objects.get(
            NIS_CPF=data['NIS_CPF']), relatorio.pessoas.all())
        # Verifica que a contagem é 1
        self.assertEqual(relatorio.pessoas.count(), 1)
