from rest_framework.serializers import SerializerMethodField
from .models import Pessoa, Relatorios, Digitador
from rest_framework import serializers  # type: ignore
from utils.CustomPagination import PessoaPagination


class PessoaSerializer(serializers.ModelSerializer):

    class Meta:
        model = Pessoa
        # fields = '__all__'
        # Trocando a lógica para personalizar a ordem da saída:
        fields = [
            'NdaFicha',
            'NIS_CPF',
            'Nome',
            'Endereço',
            'Ação',
            'created_at',  # Data de registro
            'Prioridade',
            'Status',
            'last_update',
            'DocType',
            'benefit_situation',
            'isUnderInvestigation'
        ]
        read_only_fields = ['created_at', "last_update"]

    def validate_NIS_CPF(self, value):
        """Verifica se o campo NIS ou CPF tem exatamente 11 caracteres."""
        if len(value) != 11:
            raise serializers.ValidationError(
                "O campo NIS ou CPF deve ter exatamente 11 caracteres.")
        return value

    """ def validate_Nome(self, value):
        # Dividir o nome em palavras
        for letter in value:
            try:
                int(letter)
            except:
                raise serializers.ValidationError(
                    "Você não pode digitar números no campo de nome!"
                )
        # Retornar o valor se a validação for bem-sucedida
        return value """

    def validate(self, data):
        """
        Verifica se os campos obrigatórios estão presentes
        apenas em criações ou quando relevantes.
        """
        if self.instance:  # Atualização parcial
            return data

        required_fields = ['NIS_CPF', 'Nome',
                           'Endereço', 'Ação', 'Prioridade', 'Status']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    {field: f'O campo {field} é obrigatório.'}
                )
        return data


class RelatoriosSerializer(serializers.ModelSerializer):
    pessoas = SerializerMethodField()
    total_pessoas = SerializerMethodField()

    class Meta:
        model = Relatorios
        fields = ['data', 'total_pessoas', 'pessoas']

    def get_pessoas(self, obj):
        request = self.context.get('request')
        paginator = PessoaPagination()

        # Pagina as pessoas relacionadas ao relatório
        pessoas_paginated = paginator.paginate_queryset(
            obj.pessoas.all(), request)

        # Serializa os dados paginados usando PessoaSerializer
        serialized_pessoas = PessoaSerializer(
            pessoas_paginated, many=True).data

        return serialized_pessoas

    def get_total_pessoas(self, obj):
        return obj.pessoas.count()

    """  return {
            "total_pessoas": obj.pessoas.count(),
            "pessoas": serialized_pessoas,
            "pagination": {
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "count": paginator.page.paginator.count,
                "num_pages": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number
            }
        } """


class DigitadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Digitador
        fields = ['username', 'password']
