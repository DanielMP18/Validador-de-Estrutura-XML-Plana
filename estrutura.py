"""

Entrada : lista de Token produzida por lexer.lex()
Saída   : (itens_ok, erros)
  - itens_ok: só os <item> estruturalmente corretos (seguem pra tipos.py)
  - erros   : SINTATICO (problema em <produtos>) e ESTRUTURA (problema num <item>)

Como funciona
  Cada token vira um SÍMBOLO ("<item>", "</id>", "TEXTO", "<*>"...), onde "*"
  é qualquer nome de tag desconhecido. O AFD lê um símbolo por vez e muda de
  estado conforme TRANSICOES. Par (estado, símbolo) fora da tabela = erro, e o
  ESTADO onde parou decide a categoria:
    - INICIO / EM_PRODUTOS / FIM        -> SINTATICO (fatal, para tudo)
    - EM_ITEM ... QTD_FECHADO           -> ESTRUTURA (descarta o item e
                                           RESSINCRONIZA no próximo item)
    - acabou o arquivo antes de FIM     -> SINTATICO "não foi fechado"

Este módulo não imprime nada; só devolve dados.
"""
from contrato import (ABRE, FECHA, TEXTO, SINTATICO, ESTRUTURA,
                      Campo, Erro, Item, Token, reconstruir)

# estados
INICIO = "INICIO"
EM_PRODUTOS = "EM_PRODUTOS"
EM_ITEM = "EM_ITEM"
ID_ABERTO, ID_TEXTO, ID_FECHADO = "ID_ABERTO", "ID_TEXTO", "ID_FECHADO"
PRECO_ABERTO, PRECO_TEXTO, PRECO_FECHADO = "PRECO_ABERTO", "PRECO_TEXTO", "PRECO_FECHADO"
QTD_ABERTO, QTD_TEXTO, QTD_FECHADO = "QTD_ABERTO", "QTD_TEXTO", "QTD_FECHADO"
FIM = "FIM"

ESTADOS_ITEM = frozenset({
    EM_ITEM, ID_ABERTO, ID_TEXTO, ID_FECHADO,
    PRECO_ABERTO, PRECO_TEXTO, PRECO_FECHADO,
    QTD_ABERTO, QTD_TEXTO, QTD_FECHADO,
})

# alfabeto (símbolos)
TAGS_CONHECIDAS = frozenset({"produtos", "item", "id", "preco", "qtd"})


def simbolo(token: Token) -> str:
    """Token -> símbolo do alfabeto do AFD."""
    if token.tipo == TEXTO:
        return "TEXTO"
    nome = token.valor if token.valor in TAGS_CONHECIDAS else "*"
    return f"<{nome}>" if token.tipo == ABRE else f"</{nome}>"


#  função de transição 
TRANSICOES = {
    (INICIO,         "<produtos>"):  EM_PRODUTOS,
    (EM_PRODUTOS,    "<item>"):      EM_ITEM,
    (EM_PRODUTOS,    "</produtos>"): FIM,

    (EM_ITEM,        "<id>"):        ID_ABERTO,
    (ID_ABERTO,      "TEXTO"):       ID_TEXTO,
    (ID_ABERTO,      "</id>"):       ID_FECHADO,    # campo vazio: o tipo rejeita depois
    (ID_TEXTO,       "</id>"):       ID_FECHADO,

    (ID_FECHADO,     "<preco>"):     PRECO_ABERTO,
    (PRECO_ABERTO,   "TEXTO"):       PRECO_TEXTO,
    (PRECO_ABERTO,   "</preco>"):    PRECO_FECHADO,
    (PRECO_TEXTO,    "</preco>"):    PRECO_FECHADO,

    (PRECO_FECHADO,  "<qtd>"):       QTD_ABERTO,
    (QTD_ABERTO,     "TEXTO"):       QTD_TEXTO,
    (QTD_ABERTO,     "</qtd>"):      QTD_FECHADO,
    (QTD_TEXTO,      "</qtd>"):      QTD_FECHADO,

    (QTD_FECHADO,    "</item>"):     EM_PRODUTOS,   # item completo: emite Item
}

ESTADO_INICIAL = INICIO
ESTADOS_FINAIS = frozenset({FIM})

# mensagens
MSG_NAO_ABERTO = "Elemento < produtos > não foi aberto."
MSG_NAO_FECHADO = "Elemento < produtos > não foi fechado."
MSG_DENTRO_PRODUTOS = "Conteúdo inesperado dentro de < produtos >."
MSG_APOS_FECHAR = "Conteúdo inesperado após o fechamento de < produtos >."


def _msg_estrutura(trecho: str) -> str:
    return f"Estrutura inválida em {trecho}."


def _sincronizar(tokens: list[Token], i: int) -> tuple[int, int]:
    """Erro dentro de um item, detectado no token i.

    Devolve (fim, proximo):
      fim     = índice do último token que pertence ao item defeituoso
      proximo = de onde o AFD continua (estado EM_PRODUTOS)

    Pontos de sincronização:
      </item>               -> pertence ao item; continua DEPOIS dele
      <item> / </produtos>  -> NÃO pertencem ao item; continua NELES
    """
    j = i
    while j < len(tokens):
        t = tokens[j]
        if t.tipo == FECHA and t.valor == "item":
            return j, j + 1
        if (t.tipo == ABRE and t.valor == "item") or (t.tipo == FECHA and t.valor == "produtos"):
            return j - 1, j
        j += 1
    return len(tokens) - 1, len(tokens)


def validar_estrutura(tokens: list[Token]) -> tuple[list[Item], list[Erro]]:
    itens: list[Item] = []
    erros: list[Erro] = []

    estado = ESTADO_INICIAL
    inicio_item = -1                  # índice do <item> corrente
    campos: dict[str, Campo] = {}     # id / preco / qtd do item corrente
    campo_atual = ""
    i = 0

    while i < len(tokens):
        tok = tokens[i]
        sim = simbolo(tok)
        prox = TRANSICOES.get((estado, sim))

        if prox is None:
            if estado in ESTADOS_ITEM:
                # Estrutura: descarta o item, ressincroniza e segue
                fim, i = _sincronizar(tokens, i)
                trecho = reconstruir(tokens[inicio_item:fim + 1])
                erros.append(Erro(tokens[inicio_item].linha, ESTRUTURA,
                                  _msg_estrutura(trecho)))
                estado = EM_PRODUTOS
                continue
            # Sintatico: fatal
            if estado == INICIO:
                msg = MSG_NAO_ABERTO
            elif estado == EM_PRODUTOS:
                msg = MSG_DENTRO_PRODUTOS
            else:  # FIM
                msg = MSG_APOS_FECHAR
            erros.append(Erro(tok.linha, SINTATICO, msg))
            return itens, erros

        # transição válida: guarda dados do item 
        if prox == EM_ITEM:
            inicio_item, campos = i, {}
        elif estado == EM_ITEM or estado in (ID_FECHADO, PRECO_FECHADO):
            campo_atual = sim[1:-1]                       # "id" | "preco" | "qtd"
            campos[campo_atual] = Campo("", tok.linha)    # vazio até aparecer TEXTO
        elif sim == "TEXTO":
            campos[campo_atual] = Campo(tok.valor, tok.linha)
        elif estado == QTD_FECHADO:                       # </item>: item completo
            itens.append(Item(
                linha=tokens[inicio_item].linha,
                trecho=reconstruir(tokens[inicio_item:i + 1]),
                id=campos["id"], preco=campos["preco"], qtd=campos["qtd"],
            ))

        estado = prox
        i += 1

    # Fim do arquivo 
    if estado in ESTADOS_ITEM:
        trecho = reconstruir(tokens[inicio_item:])
        erros.append(Erro(tokens[inicio_item].linha, ESTRUTURA, _msg_estrutura(trecho)))
        erros.append(Erro(tokens[-1].linha, SINTATICO, MSG_NAO_FECHADO))
    elif estado == EM_PRODUTOS:
        erros.append(Erro(tokens[-1].linha, SINTATICO, MSG_NAO_FECHADO))
    return itens, erros