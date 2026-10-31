from typing import NamedTuple

ABRE, FECHA, TEXTO = "ABRE", "FECHA", "TEXTO"
VAZIO, SINTATICO, ESTRUTURA, TIPO = "VAZIO", "SINTATICO", "ESTRUTURA", "TIPO"


class Token(NamedTuple):
    tipo: str
    valor: str
    linha: int


class Erro(NamedTuple):
    linha: int
    categoria: str
    mensagem: str


class Campo(NamedTuple):
    valor: str
    linha: int


class Item(NamedTuple):
    linha: int
    trecho: str
    id: Campo
    preco: Campo
    qtd: Campo


def reconstruir(tokens: list[Token]) -> str:
    partes = []
    for t in tokens:
        if t.tipo == ABRE:
            partes.append(f"<{t.valor}>")
        elif t.tipo == FECHA:
            partes.append(f"</{t.valor}>")
        else:
            partes.append(t.valor)
    return "".join(partes)


def formatar_erro(e: Erro) -> str:
    if e.categoria == VAZIO:
        return "Erro: Arquivo xml vazio"
    if e.categoria == SINTATICO:
        return f"Erro sintático: {e.mensagem}"
    return f"Erro de validação na linha {e.linha}: {e.mensagem}"