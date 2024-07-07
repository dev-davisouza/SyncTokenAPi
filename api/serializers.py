from .models import Pessoa, Relatorios
from rest_framework import serializers  # type: ignore


class PessoaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pessoa
        fields = '__all__'
        read_only_fields = ['created_at', "last_update"]

    def validate_NIS_CPF(self, value):
        """Verifica se o campo NIS ou CPF tem exatamente 11 caracteres."""
        if len(value) != 11:
            raise serializers.ValidationError(
                "O campo NIS ou CPF deve ter exatamente 11 caracteres.")
        return value

    def validate(self, data):
        """Verifica se todos os podem estar vazios."""
        required_fields = ['NIS_CPF', 'Nome',
                           'Endereço', 'Ação', 'Prioridade', 'Status']
        for field in required_fields:
            if not data.get(field):
                raise serializers.ValidationError(
                    f"O campo {field} é obrigatório e não pode estar vazio.")
        return data


class RelatoriosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relatorios
        fields = '__all__'
