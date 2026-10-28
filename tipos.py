from contrato import Erro, TIPO


def simbolo(c):
    if c == "0":
        return "0"
    if "1" <= c <= "9":
        return "1-9"
    return c  # letras, '.', espaços etc. ficam como estão


def rodar_afd(tabela, inicial, finais, s):
    estado = inicial
    for c in s:
        chave = (estado, simbolo(c))
        if chave not in tabela:
            return False
        estado = tabela[chave]
    return estado in finais


# id: PROD + 3 dígitos, exceto 000
TABELA_ID = {
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
FINAIS_ID = {"fim"}

# preco: sem zero à esquerda, exatamente 2 casas, mínimo 0.01
TABELA_PRECO = {
    ("q0", "0"): "zero",   ("q0", "1-9"): "int",
    ("int", "0"): "int",   ("int", "1-9"): "int",
    ("int", "."): "ponto",
    ("ponto", "0"): "d1",  ("ponto", "1-9"): "d1",
    ("d1", "0"): "fim",    ("d1", "1-9"): "fim",
    ("zero", "."): "zponto",
    ("zponto", "0"): "z0", ("zponto", "1-9"): "d1",
    ("z0", "1-9"): "fim",
}
FINAIS_PRECO = {"fim"}

# qtd: um ou mais dígitos (aceita 0 e zero à esquerda, sem sinal)
TABELA_QTD = {
    ("q0", "0"): "num",  ("q0", "1-9"): "num",
    ("num", "0"): "num", ("num", "1-9"): "num",
}
FINAIS_QTD = {"num"}


def validar_id(s: str) -> bool:
    return rodar_afd(TABELA_ID, "q0", FINAIS_ID, s)


def validar_preco(s: str) -> bool:
    return rodar_afd(TABELA_PRECO, "q0", FINAIS_PRECO, s)


def validar_qtd(s: str) -> bool:
    return rodar_afd(TABELA_QTD, "q0", FINAIS_QTD, s)


def validar_tipos(itens):
    erros = []
    for item in itens:
        ok = (validar_id(item.id.valor)
              and validar_preco(item.preco.valor)
              and validar_qtd(item.qtd.valor))
        if not ok:
            erros.append(Erro(linha=item.linha, categoria=TIPO,
                              mensagem=f"Tipo de dados inválido em {item.trecho}."))
    return erros