from contrato import Erro, TIPO


def simbolo(c):
    if c == "0":
        return "0"
    if "1" <= c <= "9":
        return "1-9"
    return c


def rodar_afd(transicoes, inicial, finais, s):
    estado = inicial
    for c in s:
        chave = (estado, simbolo(c))
        if chave not in transicoes:
            return False
        estado = transicoes[chave]
    return estado in finais


# id: PROD001 até PROD999
TRANSICOES_ID = {
    ("q0", "P"): "q1",
    ("q1", "R"): "q2",
    ("q2", "O"): "q3",
    ("q3", "D"): "q4",
    ("q4", "0"): "z1",  ("q4", "1-9"): "n1",
    ("z1", "0"): "z2",  ("z1", "1-9"): "n2",
    ("n1", "0"): "n2",  ("n1", "1-9"): "n2",
    ("z2", "1-9"): "fim",
    ("n2", "0"): "fim", ("n2", "1-9"): "fim",
}
INICIAL_ID = "q0"
FINAIS_ID = {"fim"}

# preco: 2 casas decimais, mínimo 0.01, sem zero à esquerda
TRANSICOES_PRECO = {
    ("q0", "0"): "zero",   ("q0", "1-9"): "int",
    ("int", "0"): "int",   ("int", "1-9"): "int",
    ("int", "."): "ponto",
    ("ponto", "0"): "d1",  ("ponto", "1-9"): "d1",
    ("d1", "0"): "fim",    ("d1", "1-9"): "fim",
    ("zero", "."): "zponto",
    ("zponto", "0"): "z0", ("zponto", "1-9"): "d1",
    ("z0", "1-9"): "fim",
}
INICIAL_PRECO = "q0"
FINAIS_PRECO = {"fim"}

# qtd: inteiro sem sinal
TRANSICOES_QTD = {
    ("q0", "0"): "num",  ("q0", "1-9"): "num",
    ("num", "0"): "num", ("num", "1-9"): "num",
}
INICIAL_QTD = "q0"
FINAIS_QTD = {"num"}


def validar_id(s):
    return rodar_afd(TRANSICOES_ID, INICIAL_ID, FINAIS_ID, s)


def validar_preco(s):
    return rodar_afd(TRANSICOES_PRECO, INICIAL_PRECO, FINAIS_PRECO, s)


def validar_qtd(s):
    return rodar_afd(TRANSICOES_QTD, INICIAL_QTD, FINAIS_QTD, s)


def validar_tipos(itens):
    erros = []
    for item in itens:
        ok = (validar_id(item.id.valor)
              and validar_preco(item.preco.valor)
              and validar_qtd(item.qtd.valor))
        if not ok:
            erros.append(Erro(item.linha, TIPO,
                              f"Tipo de dados inválido em {item.trecho}."))
    return erros


def detalhar(item):
    """Diz quais campos falharam. Só para o relatório."""
    ruins = []
    if not validar_id(item.id.valor):
        ruins.append(f"id={item.id.valor!r} (linha {item.id.linha})")
    if not validar_preco(item.preco.valor):
        ruins.append(f"preco={item.preco.valor!r} (linha {item.preco.linha})")
    if not validar_qtd(item.qtd.valor):
        ruins.append(f"qtd={item.qtd.valor!r} (linha {item.qtd.linha})")
    return "campos inválidos: " + ", ".join(ruins) if ruins else ""