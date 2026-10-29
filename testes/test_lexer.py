from contrato import ABRE, FECHA, TEXTO
from lexer import lex


def test_arquivo_vazio():
    assert lex("") == []


def test_so_espacos():
    assert lex(" \t\r\n  ") == []


def test_bom_no_inicio():
    tokens = lex("\ufeff<a></a>")

    assert [(token.tipo, token.valor, token.linha) for token in tokens] == [
        (ABRE, "a", 1),
        (FECHA, "a", 1),
    ]


def test_quebra_de_linha_crlf():
    tokens = lex("<a>\r\nx</a>")

    assert [(token.tipo, token.valor, token.linha) for token in tokens] == [
        (ABRE, "a", 1),
        (TEXTO, "\r\nx", 2),
        (FECHA, "a", 2),
    ]


def test_tag_em_varias_linhas():
    tokens = lex("<a\n b>\n  x</a>")

    assert [(token.tipo, token.valor, token.linha) for token in tokens] == [
        (ABRE, "a\n b", 1),
        (TEXTO, "\n  x", 3),
        (FECHA, "a", 3),
    ]


def test_menor_que_mal_formado():
    tokens = lex("<")

    assert [(token.tipo, token.valor, token.linha) for token in tokens] == [
        (TEXTO, "<", 1),
    ]


def test_texto_preserva_espacos():
    tokens = lex("<id> PROD999 </id>")

    assert tokens[1].valor == " PROD999 "


def test_linha_do_texto_apos_quebra():
    toks = lex("<a>\n  x</a>")
    assert toks[1].linha == 2
