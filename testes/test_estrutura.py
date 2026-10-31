"""

Usam um mini-tokenizador PRÓPRIO (função `tokens`), pra não depender do lexer:
se um teste daqui falhar, o problema está em estrutura.py.
"""
import re

import pytest

from contrato import ABRE, FECHA, TEXTO, SINTATICO, ESTRUTURA, Campo, Token
from estrutura import (validar_estrutura, MSG_NAO_ABERTO, MSG_NAO_FECHADO,
                       MSG_DENTRO_PRODUTOS, MSG_APOS_FECHAR)

_RE = re.compile(r"</?[^<>\s]+>|[^<>\s][^<>]*")


def tokens(xml: str) -> list[Token]:
    out = []
    for m in _RE.finditer(xml):
        s, linha = m.group(), xml.count("\n", 0, m.start()) + 1
        if s.startswith("</"):
            out.append(Token(FECHA, s[2:-1], linha))
        elif s.startswith("<"):
            out.append(Token(ABRE, s[1:-1], linha))
        else:
            out.append(Token(TEXTO, s.rstrip(), linha))
    return out


def item(i="PROD999", p="149.90", q="15") -> str:
    return f"<item><id>{i}</id><preco>{p}</preco><qtd>{q}</qtd></item>"


def doc(*partes: str) -> str:
    return "<produtos>" + "".join(partes) + "</produtos>"


def rodar(xml: str):
    return validar_estrutura(tokens(xml))


# válidos
def test_um_item_valido():
    itens, erros = rodar(doc(item()))
    assert erros == []
    assert len(itens) == 1
    it = itens[0]
    assert it.linha == 1
    assert it.trecho == item()
    assert it.id == Campo("PROD999", 1)
    assert it.preco == Campo("149.90", 1)
    assert it.qtd == Campo("15", 1)


def test_dois_itens_com_linhas():
    xml = f"<produtos>\n {item('PROD999')}\n {item('PROD123', '25.00', '200')}\n</produtos>"
    itens, erros = rodar(xml)
    assert erros == []
    assert [i.linha for i in itens] == [2, 3]
    assert [i.id.valor for i in itens] == ["PROD999", "PROD123"]
    assert itens[1].qtd == Campo("200", 3)


def test_produtos_vazio_e_valido():
    assert rodar("<produtos></produtos>") == ([], [])


def test_campo_vazio_passa_na_estrutura():
    itens, erros = rodar(doc("<item><id></id><preco>1.00</preco><qtd></qtd></item>"))
    assert erros == []
    assert itens[0].id.valor == ""
    assert itens[0].qtd.valor == ""


def test_valores_ruins_passam_na_estrutura():
    """Quem rejeita valor é a pessoa 3; aqui só importa a estrutura."""
    itens, erros = rodar(doc(item("XYZ", "abc", "1.5")))
    assert erros == [] and len(itens) == 1


#  ESTRUTURA 
ITENS_RUINS = {
    "sem_id": "<item><preco>1.00</preco><qtd>1</qtd></item>",
    "sem_preco": "<item><id>PROD001</id><qtd>1</qtd></item>",
    "sem_qtd": "<item><id>PROD001</id><preco>1.00</preco></item>",
    "tag_extra": "<item><id>PROD001</id><preco>1.00</preco><qtd>1</qtd><x>1</x></item>",
    "tag_desconhecida": "<item><foo>1</foo></item>",
    "ordem_trocada": "<item><preco>1.00</preco><id>PROD001</id><qtd>1</qtd></item>",
    "id_duplicado": "<item><id>PROD001</id><id>PROD002</id><preco>1.00</preco><qtd>1</qtd></item>",
    "item_vazio": "<item></item>",
    "texto_solto_no_item": "<item>abc<id>PROD001</id><preco>1.00</preco><qtd>1</qtd></item>",
    "fechamento_errado_enunciado": "<item><id>PROD999</id><preco>149.90</preco><qtd>15</item>",
    "tag_interna_nao_fechada": "<item><id>PROD001</id><preco>1.00<qtd>1</qtd></item>",
    "tag_interna_fechada_errada": "<item><id>PROD001</id><preco>1.00</qtd><qtd>1</qtd></item>",
}


@pytest.mark.parametrize("ruim", ITENS_RUINS.values(), ids=ITENS_RUINS.keys())
def test_item_estruturalmente_invalido(ruim):
    itens, erros = rodar(doc(ruim))
    assert itens == []
    assert len(erros) == 1
    e = erros[0]
    assert e.categoria == ESTRUTURA
    assert e.linha == 1
    assert e.mensagem == f"Estrutura inválida em {ruim}."


def test_erro_usa_linha_do_item_nao_do_token_do_erro():
    xml = "<produtos>\n<item>\n<id>PROD001</id>\n<qtd>1</qtd>\n</item>\n</produtos>"
    _, erros = rodar(xml)
    assert len(erros) == 1 and erros[0].linha == 2


def test_item_sem_fechar_seguido_de_item_valido():
    aberto = "<item><id>PROD001</id><preco>1.00</preco><qtd>1</qtd>"
    itens, erros = rodar(doc(aberto, item("PROD002")))
    assert [i.id.valor for i in itens] == ["PROD002"]
    assert len(erros) == 1
    assert erros[0].categoria == ESTRUTURA
    assert erros[0].mensagem == f"Estrutura inválida em {aberto}."


def test_item_aninhado():
    aberto = "<item><id>PROD001</id>"
    itens, erros = rodar(doc(aberto, item("PROD002")))
    assert [i.id.valor for i in itens] == ["PROD002"]
    assert [e.categoria for e in erros] == [ESTRUTURA]


def test_item_sem_fechar_antes_de_fechar_produtos():
    itens, erros = rodar("<produtos><item><id>PROD001</id></produtos>")
    assert itens == []
    assert [e.categoria for e in erros] == [ESTRUTURA]      # produtos fechou OK


def test_item_sem_fechar_no_fim_do_arquivo():
    itens, erros = rodar("<produtos><item><id>PROD001</id>")
    assert itens == []
    assert [e.categoria for e in erros] == [ESTRUTURA, SINTATICO]
    assert erros[0].mensagem == "Estrutura inválida em <item><id>PROD001</id>."
    assert erros[1].mensagem == MSG_NAO_FECHADO


#  SINTATICO
def test_produtos_nao_aberto():
    itens, erros = rodar(item() + "</produtos>")
    assert itens == []
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_NAO_ABERTO)]


def test_raiz_com_outro_nome():
    _, erros = rodar("<lista>" + item() + "</lista>")
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_NAO_ABERTO)]


def test_produtos_nao_fechado_mantem_itens_lidos():
    itens, erros = rodar("<produtos>" + item())
    assert len(itens) == 1
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_NAO_FECHADO)]


def test_produtos_sem_nada_dentro_e_sem_fechar():
    _, erros = rodar("<produtos>")
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_NAO_FECHADO)]


def test_conteudo_depois_de_fechar_produtos():
    itens, erros = rodar(doc(item()) + "<x>")
    assert len(itens) == 1
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_APOS_FECHAR)]


def test_produtos_fechado_duas_vezes():
    _, erros = rodar(doc(item()) + "</produtos>")
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_APOS_FECHAR)]


def test_texto_solto_dentro_de_produtos_e_fatal():
    itens, erros = rodar("<produtos>abc" + item() + "</produtos>")
    assert itens == []
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_DENTRO_PRODUTOS)]


def test_tag_desconhecida_entre_itens_e_fatal():
    _, erros = rodar("<produtos>" + item() + "<ITEM></ITEM></produtos>")
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_DENTRO_PRODUTOS)]


def test_produtos_dentro_de_produtos():
    _, erros = rodar("<produtos><produtos></produtos></produtos>")
    assert [(e.categoria, e.mensagem) for e in erros] == [(SINTATICO, MSG_DENTRO_PRODUTOS)]


#  recuperação
def test_tres_itens_com_o_do_meio_invalido():
    ruim = "<item><id>PROD002</id><qtd>1</qtd></item>"
    xml = f"<produtos>\n{item('PROD001')}\n{ruim}\n{item('PROD003')}\n</produtos>"
    itens, erros = rodar(xml)
    assert [i.id.valor for i in itens] == ["PROD001", "PROD003"]
    assert [(e.linha, e.categoria) for e in erros] == [(3, ESTRUTURA)]


def test_dois_itens_invalidos_geram_dois_erros():
    r1 = "<item><id>PROD001</id></item>"
    r2 = "<item></item>"
    xml = f"<produtos>\n{r1}\n{item()}\n{r2}\n</produtos>"
    itens, erros = rodar(xml)
    assert len(itens) == 1
    assert [(e.linha, e.categoria) for e in erros] == [(2, ESTRUTURA), (4, ESTRUTURA)]


def test_erro_fatal_nao_gera_erros_fantasma():
    ruim = "<item><id>PROD001</id></item>"
    itens, erros = rodar("<produtos>" + ruim + "xyz" + item() + "</produtos>")
    assert itens == []
    assert [e.categoria for e in erros] == [ESTRUTURA, SINTATICO]


def test_varios_itens_validos_depois_de_um_ruim():
    ruim = "<item><id>PROD001</id></item>"
    itens, erros = rodar(doc(ruim, item("PROD002"), item("PROD003"), item("PROD004")))
    assert [i.id.valor for i in itens] == ["PROD002", "PROD003", "PROD004"]
    assert len(erros) == 1


#  invariantes
def test_lista_vazia_nao_quebra():
    assert validar_estrutura([]) == ([], [])


def test_nao_imprime_nada(capsys):
    rodar(doc(item(), "<item></item>"))
    rodar("<produtos>")
    assert capsys.readouterr().out == ""


@pytest.mark.parametrize("xml", [
    doc(item()), doc(*ITENS_RUINS.values()), "<produtos>", "<a><b>", doc(item()) + "x",
    "<produtos><item>", "<produtos><item><id>", "</item>",
])
def test_invariantes_gerais(xml):
    itens, erros = rodar(xml)
    for it in itens:                                    # item de saída é sempre completo
        assert it.id and it.preco and it.qtd and it.trecho.startswith("<item>")
    for e in erros:                                     # só categorias da pessoa 2
        assert e.categoria in (SINTATICO, ESTRUTURA)
        assert e.linha >= 1 and e.mensagem