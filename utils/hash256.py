import hashlib
import re


def hash256(input_value: str) -> str:
    """
    Gera um hash SHA-256 (em formato hexadecimal) de 64 caracteres se
    a entrada não for um hash válido.
    Caso a entrada já seja um hash SHA-256 hexadecimal válido,
    retorna-a diretamente.

    :param input_value: Valor de entrada (texto ou hash).
    :return: Um hash SHA-256 de 64 caracteres.
    """
    # Expressão regular para verificar se é um hash SHA-256 hexadecimal válido
    sha256_pattern = re.compile(r"^[a-f0-9]{64}$", re.IGNORECASE)

    # Verifica se a entrada já é um hash SHA-256 válido
    if sha256_pattern.fullmatch(input_value):
        return input_value

    # Caso contrário, gera um hash SHA-256 do valor
    hash_object = hashlib.sha256(input_value.encode('utf-8'))
    return hash_object.hexdigest()
