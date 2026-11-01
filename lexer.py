"""
lexer.py
lex(texto) -> list[Token]

Regras (conforme o contrato):
  - arquivo vazio / só espaços e quebras -> []
  - espaços e quebras ENTRE tags não geram token
  - ABRE/FECHA: valor = nome da tag sem < > (ex: "item")
  - TEXTO: valor = texto cru entre tags (não é feito strip, para que
    " PROD001" seja rejeitado pelos AFDs de tipo)
  - linha de cada token começa em 1 (linha onde o token começa)
  - o lexer não valida nada e não imprime nada; só devolve tokens

Casos malformados (o lexer não gera erro, só tokeniza de forma segura):
  - '<' sem '>' correspondente (ou com outro '<' antes do '>') é tratado
    como parte de um TEXTO, e a pessoa 2 acusa o erro de estrutura.
"""
from contrato import ABRE, FECHA, TEXTO, Token


def lex(texto: str) -> list[Token]:
    if texto.startswith("\ufeff"):
        texto = texto[1:]
    tokens: list[Token] = []
    n = len(texto)
    i = 0
    linha = 1

    while i < n:
        if texto[i] == "<":
            fim = texto.find(">", i + 1)
            outro = texto.find("<", i + 1)
            if fim != -1 and (outro == -1 or fim < outro):
                interno = texto[i + 1:fim]
                if interno.startswith("/"):
                    tipo, nome = FECHA, interno[1:].strip()
                else:
                    tipo, nome = ABRE, interno.strip()
                tokens.append(Token(tipo, nome, linha))
                linha += interno.count("\n")
                i = fim + 1
                continue
            j = outro if outro != -1 else n
        else:
            prox = texto.find("<", i)
            j = prox if prox != -1 else n

        trecho = texto[i:j]
        if trecho.strip():
            if tokens and tokens[-1].tipo == TEXTO:
                anterior = tokens[-1]
                tokens[-1] = Token(TEXTO, anterior.valor + trecho, anterior.linha)
            else:
                prefixo = trecho[:len(trecho) - len(trecho.lstrip())]
                tokens.append(Token(TEXTO, trecho, linha + prefixo.count("\n")))
        linha += trecho.count("\n")
        i = j

    return tokens
