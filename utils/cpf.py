import random


def generate_cpf():
    """Cria uma sequência numérica de 11 números aleatoriamente."""
    cpf = [random.randint(0, 9) for _ in range(9)]

    for _ in range(2):
        val = sum([(len(cpf) + 1 - i) * v for i, v in enumerate(cpf)]) % 11
        cpf.append(11 - val if val > 1 else 0)

    # Formatar o CPF no formato XXX.XXX.XXX-XX
    # return '%d%d%d.%d%d%d.%d%d%d-%d%d' % tuple(cpf)

    # Retornar o CPF como uma string simples sem formatação
    return ''.join(map(str, cpf))
