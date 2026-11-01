import random
import re

import pytest

import tipos
from afd_dot import afd_para_dot
from contrato import Campo, Item, TIPO
from tipos import detalhar, validar_id, validar_preco, validar_qtd, validar_tipos


@pytest.mark.parametrize("s, esperado", [
    ("PROD001", True), ("PROD999", True), ("PROD100", True),
    ("PROD000", False), ("PROD1000", False), ("PROD01", False),
    ("prod001", False), ("", False), (" PROD001", False), ("PROD001 ", False),
])
def test_id(s, esperado):
    assert validar_id(s) == esperado


@pytest.mark.parametrize("s, esperado", [
    ("0.01", True), ("15.00", True), ("0.10", True), ("12345.99", True),
    ("0.00", False), ("15.0", False), ("15", False), ("15.000", False),
    ("007.50", False), ("-1.00", False), ("1,50", False),
    ("", False), (" 15.00", False), ("15.00 ", False),
])
def test_preco(s, esperado):
    assert validar_preco(s) == esperado


@pytest.mark.parametrize("s, esperado", [
    ("0", True), ("10", True), ("007", True),
    ("-1", False), ("1.5", False), ("+3", False),
    ("", False), (" 5", False), ("5 ", False),
])
def test_qtd(s, esperado):
    assert validar_qtd(s) == esperado


def item(id_, preco, qtd, linha=2):
    trecho = f"<item><id>{id_}</id><preco>{preco}</preco><qtd>{qtd}</qtd></item>"
    return Item(linha, trecho, Campo(id_, linha + 1),
                Campo(preco, linha + 2), Campo(qtd, linha + 3))


def test_item_valido_nao_gera_erro():
    assert validar_tipos([item("PROD001", "10.50", "3")]) == []


def test_um_erro_por_item():
    erros = validar_tipos([item("PROD000", "0.00", "-1", linha=7)])
    assert len(erros) == 1
    assert erros[0].linha == 7
    assert erros[0].categoria == TIPO
    assert erros[0].mensagem == f"Tipo de dados inválido em {item('PROD000', '0.00', '-1').trecho}."


def test_varios_itens():
    itens = [item("PROD001", "1.00", "1", 2),
             item("PROD000", "1.00", "1", 8),
             item("PROD002", "1.0", "1", 14)]
    assert [e.linha for e in validar_tipos(itens)] == [8, 14]


def test_detalhar():
    d = detalhar(item("PROD001", "15.0", "x"))
    assert "preco='15.0'" in d and "qtd='x'" in d and "id=" not in d
    assert detalhar(item("PROD001", "15.00", "1")) == ""


RE_ID = re.compile(r"PROD(?!000)[0-9]{3}")
RE_PRECO = re.compile(r"(?!0\.00$)(0|[1-9][0-9]*)\.[0-9]{2}")
RE_QTD = re.compile(r"[0-9]+")
ALFABETO = "PROD0123456789.-+ ,a"


def aleatoria(rnd):
    base = rnd.choice(["", "PROD", "0.", "1", "0"])
    return base + "".join(rnd.choice(ALFABETO) for _ in range(rnd.randint(0, 6)))


@pytest.mark.parametrize("funcao, regex", [
    (validar_id, RE_ID), (validar_preco, RE_PRECO), (validar_qtd, RE_QTD),
])
def test_afd_igual_regex(funcao, regex):
    rnd = random.Random(42)
    for _ in range(20000):
        s = aleatoria(rnd)
        assert funcao(s) == (regex.fullmatch(s) is not None), repr(s)


def test_afd_dot():
    dot = afd_para_dot(tipos.TRANSICOES_QTD, tipos.INICIAL_QTD, tipos.FINAIS_QTD, "qtd")
    assert dot.startswith('digraph "qtd"')
    assert '"num" [shape=doublecircle]' in dot
    assert 'inicio -> "q0"' in dot
    assert '"q0" -> "num" [label="0, 1-9"]' in dot